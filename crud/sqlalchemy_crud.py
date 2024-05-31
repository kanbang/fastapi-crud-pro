from datetime import datetime
from typing import Any, AsyncGenerator, Callable, List, Tuple, Type, Generator, Optional, TypeVar, Union

from fastapi import Depends, HTTPException, Query, Request
from pydantic import BaseModel

from sqlalchemy import delete, desc, func, literal_column, select, update, text
from sqlalchemy.orm import selectinload, Relationship, noload, DeclarativeBase
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta as Model

# sqlite only
# sqlalchemy 'Insert' object has no attribute 'on_conflict_do_update'
from sqlalchemy.dialects.sqlite import insert

from ._base import CRUDGenerator, NOT_FOUND
from ._utils import get_pk_type, resp_success

from ._types import (
    DEPENDENCIES,
    PAGINATION,
    PYDANTIC_SCHEMA as SCHEMA,
    RespModelT,
    UserDataOption,
    UserDataFilter,
    UserDataFilterSelf,
    IdNotExist,
    InvalidQueryException,
)


CALLABLE = Callable[..., RespModelT[Any]]

# Mapping of operators to SQL operators
operator_mapping = {
    "=": "=",
    "!=": "!=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "like": "LIKE",
    "in": "IN",
}


def parse_query(
    query: List[Tuple[str, str, Union[str, int, float, datetime]]], sql_query
):
    sqlalchemy_conditions = []

    for condition in query:
        if len(condition) != 3:
            raise InvalidQueryException

        field, operator, value = condition

        if operator not in operator_mapping:
            raise InvalidQueryException

        if operator == "like":
            value = f'"%{value}%"'
        elif operator == "in":
            formatted_list = [
                f'"{item}"' if isinstance(item, str) else str(item) for item in value
            ]
            value = f'({",".join(formatted_list)})'  # Convert the list to a comma-separated string
        elif isinstance(value, str):  # Check if value is a string
            value = f'"{value}"'  # Wrap string value in quotes
        elif isinstance(value, datetime):
            value = f'"{value}"'

        sqlalchemy_conditions.append(
            text(f"{field} {operator_mapping[operator]} {value}")
        )

    # and
    return sql_query.filter(*sqlalchemy_conditions)
    # or
    # return sql_query.filter(or_(*sqlalchemy_conditions))


"""
# Example query: [["age", ">=", 25], ["name", "=", "Alice"]]
[["age", ">", 9], ["name", "=", "n1"]]
[["name", "like", "n"]]

"""


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
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

# 使用pydantic约束
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
    elif isinstance(data, DeclarativeBase):
        if relationships:
            return pydantic_model.model_validate(
                model_to_dict_relation(data)
            ).model_dump()
        else:
            return pydantic_model.model_validate(
                model_to_dict_no_relation(data)
            ).model_dump()
    else:
        raise ValueError("Invalid input data type")
    

async def get_total_count(db: AsyncSession, query) -> int:
    count_subquery = (
        query.order_by(None).offset(None).limit(None).options(noload("*")).subquery()
    )
    count_query = select(func.count(literal_column("*"))).select_from(count_subquery)
    (total,) = (await db.execute(count_query)).scalars()
    return total


class SQLAlchemyCRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Model,
        db: Callable[[], AsyncGenerator[AsyncSession, None]],
        user_data_option: UserDataOption = UserDataOption.ALL_ONLY,
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        kcreate_route: Union[bool, DEPENDENCIES] = True,
        kdelete_route: Union[bool, DEPENDENCIES] = True,
        kdelete_all_route: Union[bool, DEPENDENCIES] = True,
        kupdate_route: Union[bool, DEPENDENCIES] = True,
        kget_by_id_route: Union[bool, DEPENDENCIES] = True,
        kget_one_by_filter_route: Union[bool, DEPENDENCIES] = True,
        klist_route: Union[bool, DEPENDENCIES] = True,
        kquery_route: Union[bool, DEPENDENCIES] = True,
        kquery_ex_route: Union[bool, DEPENDENCIES] = True,
        kupsert_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any,
    ) -> None:
        self.db_model = db_model
        self.db_func = db
        self._pk: str = db_model.__table__.primary_key.columns.keys()[0]
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            user_data_option=user_data_option,
            prefix=prefix or db_model.__tablename__,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            kcreate_route=kcreate_route,
            kdelete_route=kdelete_route,
            kdelete_all_route=kdelete_all_route,
            kupdate_route=kupdate_route,
            kget_by_id_route=kget_by_id_route,
            kget_one_by_filter_route=kget_one_by_filter_route,
            klist_route=klist_route,
            kquery_route=kquery_route,
            kquery_ex_route=kquery_ex_route,
            kupsert_route=kupsert_route,
            **kwargs,
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            db: AsyncSession = Depends(self.db_func),
            pagination: PAGINATION = self.pagination,
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)
            sql_query = sql_query.offset(skip).limit(limit)

            total = await get_total_count(db, sql_query)

            raw_models = await db.execute(sql_query)
            models: List[Model] = raw_models.scalars().fetchall()

            return resp_success(
                convert_to_pydantic(models, self.schema), total=total
            )

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: AsyncSession = Depends(self.db_func)  # type: ignore
        ) -> RespModelT[Optional[self.schema]]:
            sql_query = select(self.db_model).where(
                getattr(self.db_model, self._pk) == item_id,
                self.db_model.enabled_flag == 1,
            )
            raw_models = await db.execute(sql_query)
            model: Model = raw_models.scalars().first()

            if model:
                return resp_success(convert_to_pydantic(model, self.schema))
            else:
                raise IdNotExist() from None

        return route


    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            model: self.create_schema,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[self.schema]]:
            try:
                db_model: Model = self.db_model(**model.dict())
                db.add(db_model)
                db.commit()
                db.refresh(db_model)
                return resp_success(convert_to_pydantic(db_model, self.schema))
            except IntegrityError:
                db.rollback()
                raise HTTPException(422, "Key already exists") from None

        return route
    
    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            request: Request,
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[self.schema]]:
            raw_to_update = await db.get(self.db_model, item_id)
            if raw_to_update:
                model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)
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

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(db: AsyncSession = Depends(self.db_func)) -> RespModelT[Optional[int]]:
            stmt = delete(self.db_model)
            result = await db.execute(stmt)
            return resp_success(result.rowcount)
        
        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: AsyncSession = Depends(self.db_func)  # type: ignore
        ) -> RespModelT[Optional[bool]]:
            stmt = delete(self.db_model).where(
                    getattr(self.db_model, self._pk) == item_id
                )
          
            result = await db.execute(stmt)
            return resp_success(bool(result.rowcount))

        return route

    #################################################################################
    def _kcreate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            request: Request,
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[self.schema]]:
            model_dict = model.model_dump(exclude={self._pk}, exclude_none=True)
            params = await self.handle_data(model_dict, True, request)

            try:
                db_model = self.db_model(**params)
                db.add(db_model)
                await db.commit()
                await db.refresh(db_model)
                return resp_success(convert_to_pydantic(db_model, self.schema))
            except IntegrityError:
                db.rollback()
                raise HTTPException(422, "Key already exists") from None

        return route

    def _kdelete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,
            _hard: bool = True,
            db: AsyncSession = Depends(self.db_func),  # type: ignore
        ) -> RespModelT[Optional[bool]]:
            if _hard is False:
                stmt = (
                    update(self.db_model)
                    .where(
                        getattr(self.db_model, self._pk) == item_id,
                        self.db_model.enabled_flag == 1,
                    )
                    .values(enabled_flag=0)
                )
            else:
                stmt = delete(self.db_model).where(
                    getattr(self.db_model, self._pk) == item_id
                )

            result = await db.execute(stmt)
            return resp_success(bool(result.rowcount))

        return route

    def _kdelete_all(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            _hard: bool = True, db: AsyncSession = Depends(self.db_func)
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
            db: AsyncSession = Depends(self.db_func),
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
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[self.schema]]:
            filter_dict = filter.model_dump(exclude_none=True)

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, 'user_id'):
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

    def __autoload_options(self, sql_query):
        # relationships include Relationship和RelationshipProperty
        # mapper = inspect(self.db_model)
        # for prop in mapper.relationships:
        #     related_model = prop.mapper.class_
        #     sql_query = sql_query.options(
        #         selectinload(getattr(self.db_model, prop.key))
        #     )

        # Relationship、RelationshipProperty is different
        for prop in self.db_model.__mapper__.iterate_properties:
            if isinstance(prop, Relationship):
                sql_query = sql_query.options(
                    selectinload(getattr(self.db_model, prop.key))
                )
        return sql_query

    # list
    def _klist(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, 'user_id'):
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

    # filter
    def _kquery(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            filter: self.filter_schema,  # type: ignore
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[List[self.schema]]]:
            filter_dict = filter.model_dump(exclude_none=True)
            skip, limit = pagination.get("skip"), pagination.get("limit")

            sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

            if (
                user_data_filter == UserDataFilter.SELF_DATA
                or user_data_filter == UserDataFilterSelf.SELF_DATA
            ):
                if hasattr(request.state, 'user_id'):
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

    # filter plus
    # Example query: [["age", ">=", 25], ["name", "=", "Alice"]]
    def _kquery_ex(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            query: List[Tuple[str, str, Union[str, int, float, datetime, List[Any]]]],
            request: Request,
            pagination: PAGINATION = self.pagination,
            sort_by: str = Query(None, description="Sort records by this field"),
            relationships: bool = False,
            user_data_filter: self.user_data_filter_type = self.user_data_filter_defv,
            db: AsyncSession = Depends(self.db_func),
        ) -> RespModelT[Optional[List[self.schema]]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            try:
                sql_query = select(self.db_model).where(self.db_model.enabled_flag == 1)

                if (
                    user_data_filter == UserDataFilter.SELF_DATA
                    or user_data_filter == UserDataFilterSelf.SELF_DATA
                ):
                    if hasattr(request.state, 'user_id'):
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

    # Insert on Duplicate Key Update
    def _kupsert(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,  # type: ignore
            request: Request,
            db: AsyncSession = Depends(self.db_func),
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
            params["trace_id"] = getattr(request.state, 'trace_id', 0)

            # User Info
            user_id = getattr(request.state, 'user_id', 0)

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


# TODO 自动添加外键

# from sqlalchemy.orm import joinedload, selectinload
# from sqlalchemy.orm.properties import RelationshipProperty
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class AutoLoadMixin:
#     @classmethod
#     def query_with_autoload(cls, session):
#         query = session.query(cls)
#         for prop in cls.__mapper__.iterate_properties:
#             if isinstance(prop, RelationshipProperty):
#                 # 判断是否需要自动加载关联数据
#                 if getattr(cls, prop.key).autoload:
#                     query = query.options(selectinload(getattr(cls, prop.key)))
#         return query

# # 示例 User 模型
# class User(Base, AutoLoadMixin):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)

#     addresses = relationship("Address", back_populates="user", autoload=True)

# # 使用
# user = User.query_with_autoload(session).filter_by(name='John').first()


"""


    def _kupdate(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.schema,
            db: Session = Depends(self.db_func),
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

                for rkey, rval in relation_field.items():
                    prop = self.db_model.__mapper__.get_property(rkey)
                    if isinstance(prop, Relationship):
                        rclass = prop.mapper.class_
                        rpk: str = rclass.__table__.primary_key.columns.keys()[0]

                        # rlist = getattr(raw_to_update, rkey)
                        rmodel_list = []
                        for rid in rval:
                            rmodel: rclass = (
                                (
                                    await db.execute(
                                        select(rclass).where(
                                            getattr(rclass, rpk) == rid
                                        )
                                    )
                                )
                                .scalars()
                                .first()
                            )
                            if rmodel:
                                rmodel_list.append(rmodel)

                        
                        for rmodel in rmodel_list:
                            # prop.back_populates:'department'
                            setattr(rmodel, prop.back_populates, None)
                            setattr(rmodel, prop.back_populates+"_id", None)


                        await db.run_sync(lambda session: getattr(raw_to_update, rkey))
                        # await db.run_sync(lambda session: setattr(raw_to_update, rkey, []))
                        await db.run_sync(lambda session: setattr(raw_to_update, rkey, rmodel_list))
                        # setattr(raw_to_update, rkey, rmodel_list)

                        # item.owners.remove(owner)
                        # item = db.query(Item).filter(Item.id == item_id).first()
                        # owner = db.query(User).filter(User.id == owner_id).first()
                        # if item is None or owner is None:
                        # raise HTTPException(status_code=404, detail="Item or Owner not found")
                        # item.owners.append(owner)

                ##########################################################################################

                params = await self.handle_data(model_dict)

                for key, value in params.items():
                    if hasattr(raw_to_update, key):
                        setattr(raw_to_update, key, value)

                await db.commit()
                await db.refresh(raw_to_update)
                return resp_success(convert_to_pydantic(raw_to_update, self.schema))
            else:
                raise ValueError("id不存在!")

        return route

"""
