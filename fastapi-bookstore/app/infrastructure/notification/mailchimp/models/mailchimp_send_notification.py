from pydantic import BaseModel, Field, ConfigDict

class TemplateContent(BaseModel):
    name: str = Field()
    content: str = Field()

    model_config = ConfigDict(serialize_by_alias=True)

class To(BaseModel):
    email: str = Field()
    name: str = Field()

    model_config = ConfigDict(serialize_by_alias=True)

class GlobalMergeVar(BaseModel):
    name: str = Field()
    content: str = Field()

    model_config = ConfigDict(serialize_by_alias=True)

class Message(BaseModel):
    html: str | None
    text: str | None
    subject: str | None
    from_email: str | None
    publish_from_email: str | None
    from_name: str | None
    publish_from_name: str | None
    to: list[To]
    merge_language: str
    global_merge_vars: list[GlobalMergeVar]

    model_config = ConfigDict(serialize_by_alias=True)

class SendMessageWithTemplate(BaseModel):
    key: str | None
    template_name: str
    template_content: list[TemplateContent]
    message: Message
    is_async: bool | None = Field(serialization_alias="async")
    ip_pool: str | None
    send_at: str | None

    model_config = ConfigDict(serialize_by_alias=True)

    @classmethod
    def create(
            cls,
            template_name: str,
            template_content: list,
            from_email: str,
            from_name: str,
            to_email: str,
            to_name: str,
            merge_language: str,
            global_merge_vars: list
    ) :
        return cls(
            key=None,
            template_name=template_name,
            template_content=[TemplateContent(name=template["name"], content=template["content"]) for template in template_content],
            message=Message(
                html=None,
                text=None,
                subject=None,
                publish_from_email=None,
                publish_from_name=None,
                from_email=from_email,
                from_name=from_name,
                merge_language=merge_language,
                global_merge_vars=[GlobalMergeVar(name=merge_var["name"], content=merge_var["content"]) for merge_var in global_merge_vars],
                to=[To(email=to_email, name=to_name)],
            ),
            is_async=False,
            ip_pool=None,
            send_at=None,
        )
