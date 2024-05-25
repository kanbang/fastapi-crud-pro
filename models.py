from tortoise import Model, fields


class BaseModel(Model):
    """Base for all models."""

    id = fields.IntField(pk=True)
    creation_date = fields.DatetimeField(auto_now_add=True, description="创建时间")
    created_by = fields.IntField(null=True, description="创建人ID")
    updation_date = fields.DatetimeField(auto_now=True, description="更新时间")
    updated_by = fields.IntField(null=True, description="更新人ID")
    enabled_flag = fields.BooleanField(default=True, description="是否删除, 0 删除 1 非删除")
    trace_id = fields.CharField(max_length=255, null=True, description="trace_id")

    class Meta:
        abstract = True
        table_description = "Base model with common fields"
        
class PotatoModel(Model):
    thickness = fields.FloatField()
    mass = fields.FloatField()
    color = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)


class CarrotModel(Model):
    length = fields.FloatField()
    color = fields.CharField(max_length=255)
