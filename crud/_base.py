from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, Type, Union

from fastapi import APIRouter, HTTPException
from fastapi.types import DecoratedCallable

from ._types import T, DEPENDENCIES, RespModelT, UserDataOption, UserDataFilter, UserDataFilterAll, UserDataFilterSelf
from ._utils import pagination_factory, schema_factory

NOT_FOUND = HTTPException(404, "Item not found")


class IOrmImpl(ABC):
    @abstractmethod
    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    ################################################################################
    @abstractmethod
    def _kcreate(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kdelete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kdelete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kupdate(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kget_one_by_filter(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _klist(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kquery(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kquery_ex(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _kupsert(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError


class CRUDGenerator(Generic[T], APIRouter, IOrmImpl):
    schema: Type[T]
    create_schema: Type[T]
    update_schema: Type[T]
    _base_path: str = "/"

    def __init__(
        self,
        schema: Type[T],
        create_schema: Optional[Type[T]] = None,
        update_schema: Optional[Type[T]] = None,
        filter_schema: Optional[Type[T]] = None,
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

        self.schema = schema
        self.pagination = pagination_factory(max_limit=paginate)
        self._pk: str = self._pk if hasattr(self, "_pk") else "id"
        self.create_schema = (
            create_schema
            if create_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Create")
        )
        self.update_schema = (
            update_schema
            if update_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Update")
        )
        self.filter_schema = (
            filter_schema
            if filter_schema
            else schema_factory(self.schema, name="Filter")
        )

        prefix = str(prefix if prefix else self.schema.__name__).lower()
        prefix = self._base_path + prefix.strip("/")
        tags = tags or [prefix.strip("/").capitalize()]

        user_data_filter_type_dict = {
            UserDataOption.ALL_ONLY: UserDataFilterAll,
            UserDataOption.ALL_DEFAULT: UserDataFilter,
            UserDataOption.SELF_ONLY: UserDataFilterSelf,
            UserDataOption.SELF_DEFAULT: UserDataFilter,
        }

        user_data_filter_defv_dict = {
            UserDataOption.ALL_ONLY: UserDataFilterAll.ALL_DATA,
            UserDataOption.ALL_DEFAULT: UserDataFilter.ALL_DATA,
            UserDataOption.SELF_ONLY: UserDataFilterSelf.SELF_DATA,
            UserDataOption.SELF_DEFAULT: UserDataFilter.SELF_DATA,
        }

        self.user_data_filter_type = user_data_filter_type_dict[user_data_option]
        self.user_data_filter_defv = user_data_filter_defv_dict[user_data_option]

        super().__init__(prefix=prefix, tags=tags, **kwargs)

        if get_all_route:
            self._add_api_route(
                "",
                self._get_all(),
                methods=["GET"],
                response_model=Optional[List[self.schema]],  # type: ignore
                summary="Get All",
                dependencies=get_all_route,
            )

        if create_route:
            self._add_api_route(
                "",
                self._create(),
                methods=["POST"],
                response_model=self.schema,
                summary="Create One",
                dependencies=create_route,
            )

        if delete_all_route:
            self._add_api_route(
                "",
                self._delete_all(),
                methods=["DELETE"],
                response_model=Optional[List[self.schema]],  # type: ignore
                summary="Delete All",
                dependencies=delete_all_route,
            )

        if get_one_route:
            self._add_api_route(
                "/{item_id}",
                self._get_one(),
                methods=["GET"],
                response_model=self.schema,
                summary="Get One",
                dependencies=get_one_route,
                error_responses=[NOT_FOUND],
            )

        if update_route:
            self._add_api_route(
                "/{item_id}",
                self._update(),
                methods=["PUT"],
                response_model=self.schema,
                summary="Update One",
                dependencies=update_route,
                error_responses=[NOT_FOUND],
            )

        if delete_one_route:
            self._add_api_route(
                "/{item_id}",
                self._delete_one(),
                methods=["DELETE"],
                response_model=self.schema,
                summary="Delete One",
                dependencies=delete_one_route,
                error_responses=[NOT_FOUND],
            )

        ####################################################################
        if kcreate_route:
            self._add_api_route(
                "/create",
                self._kcreate(),
                methods=["POST"],
                response_model=RespModelT[Optional[self.schema]],
                summary="Create One",
                dependencies=kcreate_route,
            )

        if kdelete_route:
            self._add_api_route(
                "/delete",
                self._kdelete_one(),
                methods=["POST"],
                response_model=RespModelT[Optional[bool]],
                summary="Delete By Key",
                dependencies=kdelete_route,
            )

        if kdelete_all_route:
            self._add_api_route(
                "/delete_all",
                self._kdelete_all(),
                methods=["POST"],
                response_model=RespModelT[Optional[int]],
                summary="Delete All",
                dependencies=kdelete_all_route,
            )

        if kupdate_route:
            self._add_api_route(
                "/update",
                self._kupdate(),
                methods=["POST"],
                response_model=RespModelT[Optional[self.schema]],
                summary="Update One By Key",
                dependencies=kupdate_route,
                error_responses=[NOT_FOUND],
            )

        if kget_by_id_route:
            self._add_api_route(
                "/get_by_id",
                self._get_one(),
                methods=["POST"],
                response_model=RespModelT[Optional[self.schema]],
                summary="Get One By Filter Value",
                dependencies=kget_by_id_route,
                error_responses=[NOT_FOUND],
            )

        if kget_one_by_filter_route:
            self._add_api_route(
                "/get_one_by_filter",
                self._kget_one_by_filter(),
                methods=["POST"],
                response_model=RespModelT[Optional[self.schema]],
                summary="Get One By Filter Value",
                dependencies=kget_one_by_filter_route,
                error_responses=[NOT_FOUND],
            )

        if klist_route:
            self._add_api_route(
                "/list",
                self._klist(),
                methods=["POST"],
                response_model=RespModelT[Optional[List[self.schema]]],
                summary="List All",
                dependencies=klist_route,
                error_responses=[NOT_FOUND],
            )

        if kquery_route:
            self._add_api_route(
                "/query",
                self._kquery(),
                methods=["POST"],
                response_model=RespModelT[Optional[List[self.schema]]],
                summary="Query Many By Filter Value",
                dependencies=kquery_route,
                error_responses=[NOT_FOUND],
            )

        if kquery_ex_route:
            self._add_api_route(
                "/query_ex",
                self._kquery_ex(),
                methods=["POST"],
                response_model=RespModelT[Optional[List[self.schema]]],
                summary="Query Many By Filter Condition, [=, !=, >, <, >=, <=, like, in]",
                dependencies=kquery_ex_route,
                error_responses=[NOT_FOUND],
            )

        if kupsert_route:
            self._add_api_route(
                "/upsert",
                self._kupsert(),
                methods=["POST"],
                response_model=RespModelT[Optional[self.schema]],
                summary="Insert Or Update",
                dependencies=kupsert_route,
                error_responses=[NOT_FOUND],
            )


    def _add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        dependencies: Union[bool, DEPENDENCIES],
        error_responses: Optional[List[HTTPException]] = None,
        **kwargs: Any,
    ) -> None:
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = (
            {err.status_code: {"detail": err.detail} for err in error_responses}
            if error_responses
            else None
        )

        super().add_api_route(
            path, endpoint, dependencies=dependencies, responses=responses, **kwargs
        )

    def api_route(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                route.path == f"{self.prefix}{path}"  # type: ignore
                and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    def _raise(self, e: Exception, status_code: int = 422) -> HTTPException:
        raise HTTPException(422, ", ".join(e.args)) from e
