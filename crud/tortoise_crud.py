from datetime import datetime
from typing import Any, Callable, List, Tuple, Type, TypeVar, cast, Coroutine, Optional, Union

from fastapi import Depends, Request, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from ._base import CRUDGenerator, NOT_FOUND
from ._types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA, RespModelT, UserDataOption, UserDataFilter, UserDataFilterAll, UserDataFilterSelf
from ._utils import get_pk_type, resp_success

try:
    from tortoise.models import Model
except ImportError:
    Model = None  # type: ignore
    tortoise_installed = False
else:
    tortoise_installed = True

from tortoise.queryset import QuerySet


CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Model]]]

###########################################################################################
# Define a generic type variable
ModelType = TypeVar("ModelType", bound=Model)
PydanticType = TypeVar("PydanticType", bound=BaseModel)


def model_to_dict_no_relation(model):
    return {
        column.name: getattr(model, column.name) for column in model.__table__.columns
    }


def model_to_dict_relation(model, seen=None):
    if seen is None:
        seen = set()

    if model in seen:
        return None

    seen.add(model)

    result = {
        column.name: getattr(model, column.name) for column in model.__table__.columns
    }

    for relationship in model.__mapper__.relationships:
        try:
            related_obj = getattr(model, relationship.key)
        except Exception as e:
            result[relationship.key] = None
            continue

        if related_obj is None:
            result[relationship.key] = None
        else:
            if relationship.uselist:
                result[relationship.key] = [
                    model_to_dict_relation(item, seen) for item in related_obj
                ]
            else:
                result[relationship.key] = model_to_dict_relation(related_obj, seen)

    return result

def convert_to_pydantic(
    data: Union[dict, ModelType, List[ModelType]],
    pydantic_model: Type[PydanticType],
    relationships: bool = False,
) -> Union[PydanticType, List[PydanticType]]:
    if data is None:
        return None
    elif isinstance(data, dict):
        return pydantic_model.model_validate(data).model_dump()
    elif isinstance(data, list):
        return [
            convert_to_pydantic(item, pydantic_model, relationships) for item in data
        ]
    elif isinstance(data, Model):
        if relationships:
            return pydantic_model.model_validate(
                model_to_dict_relation(data),
            ).model_dump()
        else:
            return pydantic_model.model_validate(
                model_to_dict_no_relation(data),
            ).model_dump()
    else:
        raise ValueError("Invalid input data type")



class TortoiseCRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[Model],
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        filter_schema: Optional[Type[SCHEMA]] = None,
        user_data_option: UserDataOption = UserDataOption.ALL_ONLY,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any
    ) -> None:
        assert (
            tortoise_installed
        ), "Tortoise ORM must be installed to use the TortoiseCRUDRouter."

        self.db_model = db_model
        self._pk: str = db_model.describe()["pk_field"]["db_column"]
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            filter_schema=filter_schema,
            user_data_option=user_data_option,
            prefix=prefix or db_model.describe()["name"].replace("None.", ""),
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(pagination: PAGINATION = self.pagination) -> List[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")
            query = self.db_model.all().offset(cast(int, skip))
            if limit:
                query = query.limit(limit)
            return await query

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: int) -> Model:
            model = await self.db_model.filter(id=item_id).first()

            if model:
                return model
            else:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(model: self.create_schema) -> Model:  # type: ignore
            db_model = self.db_model(**model.dict())
            await db_model.save()

            return db_model

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: int, model: self.update_schema  # type: ignore
        ) -> Model:
            await self.db_model.filter(id=item_id).update(
                **model.dict(exclude_unset=True)
            )
            return await self._get_one()(item_id)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route() -> List[Model]:
            await self.db_model.all().delete()
            return await self._get_all()(pagination={"skip": 0, "limit": None})

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: int) -> Model:
            model: Model = await self._get_one()(item_id)
            await self.db_model.filter(id=item_id).delete()

            return model

        return route


    #################################################################################
    def _kcreate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            request: Request,
        ) -> RespModelT[Optional[self.schema]]:
            
            model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)
            db_model = self.db_model(**model_dict)
            await db_model.save()
            return resp_success(convert_to_pydantic(db_model, self.schema))

        return route
    

    def _kdelete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,
            _hard: bool = True,
        ) -> RespModelT[Optional[bool]]:
            if _hard is False:
                ret = await self.db_model.filter(**{self._pk: item_id, "enabled_flag": 1 }).update(enabled_flag=0)
            else:
                ret = self.db_model.filter(**{self._pk: item_id}).delete()

            return resp_success(bool(ret))

        return route

    def _kdelete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            _hard: bool = True, 
        ) -> RespModelT[Optional[int]]:
            if _hard is False:
                stmt = (
                    update(self.db_model)
                    .where(
                        self.db_model.enabled_flag == 1,
                    )
                    .values(enabled_flag=0)
                )
            else:
                stmt = delete(self.db_model)

            result = await db.execute(stmt)
            return resp_success(result.rowcount)

        return route

    def _kupdate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,
            request: Request,
            
        ) -> RespModelT[Optional[self.schema]]:
            raw_to_update = await db.get(self.db_model, getattr(model, self._pk))

            if raw_to_update:
                model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)

                ##########################################################################################
                # Relationships
                relation_field = {
                    key[:-7]: value
                    for key, value in model_dict.items()
                    if (
                        value
                        and key.endswith("_refids")
                        and hasattr(self.db_model, key[:-7])
                    )
                }

                for rkey, rlist in relation_field.items():
                    # 删除 relation_field, 否则 if hasattr(raw_to_update, key): 会异常
                    if rkey in model_dict:
                        del model_dict[rkey]

                    prop = self.db_model.__mapper__.get_property(rkey)
                    if isinstance(prop, Relationship):
                        rclass = prop.mapper.class_
                        rpk: str = rclass.__table__.primary_key.columns.keys()[0]

                        rmodels = await db.execute(
                            select(rclass).where(getattr(rclass, rpk).in_(rlist))
                        )

                        if prop.secondary is not None:
                            rmodel_list = rmodels.scalars().fetchall()
                            await db.run_sync(
                                lambda session: getattr(raw_to_update, rkey)
                            )
                            setattr(raw_to_update, rkey, rmodel_list)
                        else:
                            for rmodel in rmodels.scalars():
                                setattr(rmodel, prop.back_populates, raw_to_update)

                ##########################################################################################

                params = await self.handle_data(model_dict, False, request)

                for key, value in params.items():
                    if hasattr(raw_to_update, key):
                        setattr(raw_to_update, key, value)

                await db.commit()
                await db.refresh(raw_to_update)
                return resp_success(convert_to_pydantic(raw_to_update, self.schema))
            else:
                raise ValueError("id不存在!")

        return route

    # 筛选
    def _kget_one_by_filter(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter: self.filter_schema,  # type: ignore
            request: Request,
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            
        ) -> RespModelT[Optional[self.schema]]:
            filter_dict = filter.model_dump(exclude_none=True)

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                sql_query = sql_query.where(
                    self.db_model.created_by == request.state.user_id
                )

            if relationships:
                sql_query = self.__autoload_options(sql_query)

            if filter_dict:
                sql_query = sql_query.where(
                    *(
                        getattr(self.db_model, attr) == value
                        for attr, value in filter_dict.items()
                    )
                )

            raw_models = await db.execute(sql_query)
            model: Model = raw_models.scalars().first()

            if model:
                return resp_success(
                    convert_to_pydantic(model, self.schema, relationships)
                )
            else:
                raise IdNotExist() from None

        return route

    # 自动加载选项函数
    def __autoload_options(self, query: QuerySet) -> QuerySet:
        for field in self.db_model._meta.fields_map.values():
            if field.__class__.__name__ in ["BackwardFKRelation", "ForeignKeyField", "ManyToManyField"]:
                query = query.prefetch_related(field.name)
        return query

    # list
    def _klist(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            
            query = self.db_model.filter(enabled_flag=True)

            if user_data_filter == UserDataFilter.SELF_DATA:
                query = query.filter(created_by=request.state.user_id)

            if relationships:
                query = self.__autoload_options(query)

            if sort_by:
                if sort_by.startswith("-"):
                    query = query.order_by(f"-{sort_by[1:]}")
                else:
                    query = query.order_by(sort_by)

            query = query.offset(skip).limit(limit)

            total = await query.count()
            models = await MyModel_Pydantic.from_queryset(query)


            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                sql_query = sql_query.where(
                    self.db_model.created_by == request.state.user_id
                )

            if relationships:
                sql_query = self.__autoload_options(sql_query)

            if sort_by:
                if sort_by.startswith("-"):
                    sql_query = sql_query.order_by(desc(sort_by[1:]))
                else:
                    sql_query = sql_query.order_by(sort_by)

            sql_query = sql_query.offset(skip).limit(limit)

            total = await get_total_count(db, sql_query)

            raw_models = await db.execute(sql_query)
            models: List[Model] = raw_models.scalars().fetchall()

            return resp_success(
                convert_to_pydantic(models, self.schema, relationships), total=total
            )

        return route

    # 筛选
    def _kquery(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter: self.filter_schema,  # type: ignore
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            
        ) -> RespModelT[Optional[List[self.schema]]]:
            filter_dict = filter.model_dump(exclude_none=True)
            skip, limit = pagination.get("skip"), pagination.get("limit")

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                sql_query = sql_query.where(
                    self.db_model.created_by == request.state.user_id
                )

            if relationships:
                sql_query = self.__autoload_options(sql_query)

            if filter_dict:
                sql_query = sql_query.where(
                    *(
                        getattr(self.db_model, attr) == value
                        for attr, value in filter_dict.items()
                    )
                )

            if sort_by:
                if sort_by.startswith("-"):
                    sql_query = sql_query.order_by(desc(sort_by[1:]))
                else:
                    sql_query = sql_query.order_by(sort_by)

            sql_query = sql_query.offset(skip).limit(limit)

            raw_models = await db.execute(sql_query)
            raw_models: List[Model] = raw_models.scalars().fetchall()
            return resp_success(
                convert_to_pydantic(raw_models, self.schema, relationships)
            )

        return route

    # 筛选
    # Example query: [["age", ">=", 25], ["name", "=", "Alice"]]
    def _kquery_ex(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            query: List[Tuple[str, str, Union[str, int, float, datetime, List[Any]]]],
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            try:
                sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

                if (
                    user_data_filter == UserDataFilter.SELF_DATA
                    or user_data_filter == UserDataFilterSelf.SELF_DATA
                ):
                    sql_query = sql_query.where(
                        self.db_model.created_by == request.state.user_id
                    )

                if relationships:
                    sql_query = self.__autoload_options(sql_query)

                if query:
                    sql_query = parse_query(query, sql_query)

                if sort_by:
                    # ? sort_by[1:]
                    # if sort_by not in self.db_model.get_table_column_names():
                    #     raise InvalidQueryException

                    if sort_by.startswith("-"):
                        sql_query = sql_query.order_by(desc(sort_by[1:]))
                    else:
                        sql_query = sql_query.order_by(sort_by)

                sql_query = sql_query.offset(skip).limit(limit)

                raw_models = await db.execute(sql_query)
                models: List[Model] = raw_models.scalars().fetchall()
                return resp_success(
                    convert_to_pydantic(models, self.schema, relationships)
                )

            except InvalidQueryException:
                raise HTTPException(
                    status_code=400, detail="Invalid query format or sort_by field"
                )

        return route

    # 插入冲突则更新
    def _kupsert(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,  # type: ignore
            request: Request,
            
        ) -> RespModelT[Optional[self.schema]]:
            # model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)
            model_dict = model.model_dump(exclude_none=True)

            # create 不定，TODO
            params = await self.handle_data(model_dict, True, request)

            # if not isinstance(model_dict, dict):
            #     raise ValueError("更新参数错误！")

            # id = params.get("id", None)
            # params = await self.handle_data(data)

            insert_stmt = insert(self.db_model).values(**params)

            # mysql
            # on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update( **params)

            # sqlite
            # del params[self._pk]
            on_duplicate_key_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[self._pk], set_=model_dict
            )

            result = await db.execute(on_duplicate_key_stmt)
            if result.is_insert:
                (primary_key,) = result.inserted_primary_key
                model_dict[self._pk] = primary_key

            return resp_success(convert_to_pydantic(model_dict, self.schema))

        return route

    async def handle_data(
        self, data: Union[dict, list], create: bool, request: Request
    ) -> Union[dict, list]:
        """
        :param params: 参数列表
        :return: 过滤好的参数
        """
        if isinstance(data, dict):
            # 1. 只保留数据库字段
            # 2. 筛选掉的特定键列表
            keys_to_remove = ["creation_date", "updation_date", "enabled_flag"]
            params = {
                key: value
                for key, value in data.items()
                if (hasattr(self.db_model, key) and (key not in keys_to_remove))
            }

            # 添加属性
            params["trace_id"] = request.state.trace_id

            # User Info
            user_id = request.state.user_id or 0

            # if not params.get(self._pk, None):
            #     params["created_by"] = user_id

            if create:
                params["created_by"] = user_id

            params["updated_by"] = user_id

            return params

        if isinstance(data, list):
            params = [await self.handle_data(item, create, request) for item in data]
            return params

        return data