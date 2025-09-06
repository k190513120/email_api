**BaseOpenSDK（Python）官方文档**

**概述**

[飞书开放平台](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview)提供了一系列服务端的原子 API 来实现多元化的功能，其中就包括操作多维表格的数据。但是这一套流程需要申请开放平台应用，使用开放平台的鉴权体系，对于只想通过服务端脚本快速操作多维表格的开发者，流程未免显得繁琐。为此，我们新推出了多维表格独立的鉴权体系，开发者可以在网页端获取某个 Base 的授权码PersonalBaseToken，即可在服务端通过 SDK 操作 Base 数据。

[BaseOpenSDK](https://feishu.feishu.cn/docx/WL3odCnn3o42oFx2mxfcYRDgnYe) 接口定义和[飞书开放平台 OpenAPI](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview) 完全一致，无需额外的学习成本。 我们将所有冗长的逻辑内置处理，提供完备的类型系统、语义化的编程接口，提高开发者的编码体验。😙

**概念**

|     |     |     |
| --- | --- | --- |
| **术语** | **解释** | **图示** |
| Base | 多维表格文档 |     |
| AppToken （又称 BaseId） | Base 文档的唯一标识，可从 Base URL 路径参数 /base/:app_token快速获得（图一）；但如果是 /wiki/ 路径，则不能便捷获得。<br><br>因此，我们建议直接通过[【开发工具】插件](https://feishu.feishu.cn/base/extension/replit_3c13eb5bb6ae63e6) 快速获取当前 Base 的 AppToken （又称 BaseId，见图二）。 |     |
| PersonalBaseToken | Base 文档授权码。用户针对某个 Base 文档生成的鉴权凭证，使用凭证访问相应的接口可对 Base 数据进行读写。<br><br>注：使用 PersonalBaseToken 访问 OpenAPI 单文档限频 2qps，多文档支持并发。<br><br>( [PersonalBaseToken 使用指南](https://feishu.feishu.cn/docx/Samyd47njoe46wx6cgWcDIywnZZ) ) |     |

**安装**

本 SDK 支持 Python 3。

pip

Shell  
pip install https://lf3-static.bytednsdoc.com/obj/eden-cn/lmeh7phbozvhoz/base-open-sdk/baseopensdk-0.0.13-py3-none-any.whl

poetry

Shell  
poetry add https://lf3-static.bytednsdoc.com/obj/eden-cn/lmeh7phbozvhoz/base-open-sdk/baseopensdk-0.0.13-py3-none-any.whl

**如何使用**

SDK 提供了语义化的调用方式，只需要提供相关参数创建 client 实例，接着使用其上的语义化方法client.\[业务域\].\[接口版本号\].\[资源\].\[方法\]即可完成 API 调用。例如列出 Base 数据表记录：

Python  
_from baseopensdk import BaseClient, JSON  
from baseopensdk.api.base.v1 import \*  
from dotenv import load_dotenv, find_dotenv  
import os  
<br/>load_dotenv(find_dotenv())  
<br/>APP_TOKEN = os.environ\['APP_TOKEN'\]  
PERSONAL_BASE_TOKEN = os.environ\['PERSONAL_BASE_TOKEN'\]  
TABLE_ID = os.environ\['TABLE_ID'\]_  
<br/>\# 构建client  
client: BaseClient = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.build()  
<br/>\# 构造请求对象  
request = ListAppTableRecordRequest.builder() \\  
.table_id(TABLE_ID) \\  
.page_size(20) \\  
.build()  
<br/>\# 发起请求  
response = client.base.v1.app_table_record.list(request)  
<br/>\# 打印序列化数据  
print(JSON.marshal(response.data, indent=4))

**BaseClient构造参数：**

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **参数** | **描述** | **类型** | **必须** | **默认** |
| app_token | Base 文档的唯一标识，从 Base 网页的路径参数获取 /base/:app_token | str | 是   | \-  |
| personal_base_token | Base 文档授权码。从 Base 网页端 获取（如下图） | str | 是   | \-  |
| domain | 域名  | FEISHU_DOMAIN/  <br>LARK_DOMAIN | 否   | FEISHU_DOMAIN |
| log_level | 日志级别 | LogLevel | 否   | LogLevel.INFO |

**使用海外 Lark OpenAPI 服务**

domain 默认为 FEISHU_DOMAIN，可手动改为 LARK_DOMAIN

Python  
_from baseopensdk import BaseClient, LARK_DOMAIN_  
<br/>\# 构建client  
client: BaseClient = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.domain(_LARK_DOMAIN_)  
.build()

**附件上传**

和调用普通 API 的方式一样，按类型提示传递参数即可

Python  
from baseopensdk import BaseClient  
from baseopensdk.api.drive.v1 import \*  
from dotenv import load_dotenv, find_dotenv  
import os  
<br/>load_dotenv(find_dotenv())  
<br/>APP_TOKEN = os.environ\['APP_TOKEN'\]  
PERSONAL_BASE_TOKEN = os.environ\['PERSONAL_BASE_TOKEN'\]  
TABLE_ID = os.environ\['TABLE_ID'\]  
<br/>client = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.build()  
<br/><br/>\# 构造请求对象  
file_name = 'test.txt'  
path = os.path.abspath(file_name)  
file = open(path, "rb")  
request = UploadAllMediaRequest.builder() \\  
.request_body(UploadAllMediaRequestBody.builder()  
.file_name(file_name)  
.parent_type("bitable_file")  
.parent_node(APP_TOKEN)  
.size(os.path.getsize(path))  
.file(file)  
.build()) \\  
.build()  
<br/>\# 发起请求  
response: UploadAllMediaResponse = client.drive.v1.media.upload_all(request)  
<br/>file_token = response.data.file_token  
print(file_token)

上传附件后添加到新建记录的附件字段

Python  
\# 构造请求对象  
request = UpdateAppTableRecordRequest.builder() \\  
.table_id(TABLE_ID) \\  
.record_id(RECORD_ID) \\  
.request_body(AppTableRecord.builder()  
.fields({  
"附件": \[{"file_token": file_token}\] # 👆🏻前面接口返回的 file_token  
})  
.build()) \\  
.build()  
<br/>\# 发起请求  
response: UpdateAppTableRecordResponse = client.base.v1.app_table_record.update(request)

**附件下载**

Python  
<br/>from baseopensdk import BaseClient  
from baseopensdk.api.drive.v1 import \*  
from dotenv import load_dotenv, find_dotenv  
import os  
import json  
<br/>load_dotenv(find_dotenv())  
<br/>APP_TOKEN = os.environ\['APP_TOKEN'\]  
PERSONAL_BASE_TOKEN = os.environ\['PERSONAL_BASE_TOKEN'\]  
TABLE_ID = os.environ\['TABLE_ID'\]  
<br/>\# 构建client  
client = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.build()  
<br/>\# 高级权限鉴权信息 文档未开启高级权限则无需传 extra 字段  
extra = json.dumps({  
"bitablePerm": {  
"tableId": TABLE_ID, # 附件所在数据表 id  
"attachments": {  
FIELD_ID: { # 附件字段 id  
RECORD_ID: \[ # 附件所在记录 record_id  
FILE_TOKEN # 附件 file_token  
\]  
}  
}  
}  
})  
<br/>\# 构造请求对象  
request = DownloadMediaRequest.builder() \\  
.file_token(FILE_TOKEN) \\  
.extra(extra) \\  
.build()  
<br/>\# 发起请求  
response = client.drive.v1.media.download(request)  
<br/>\# 保存文件到本地  
f = open(f"{response.file_name}", "wb")  
f.write(response.file.read())  
f.close()

**接口范围列表**

|     |     |     |     |
| --- | --- | --- | --- |
| **业务域** | **资源** | **方法** | 调用**示例** |
| base（多维表格） | app（多维表格） | [copy](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/copy)、[~~create~~](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/create)、[get](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/get)、[update](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/update) | 拷贝多维表格：client.base.app.copy() |
|     | appDashboard（仪表盘） | [copy](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-dashboard/copy)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-dashboard/list) | 拷贝仪表盘：<br><br>client.base.appDashboard.copy() |
|     | appRole（自定义角色） | [create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role/delete)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role/list)、[update](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role/update) |     |
|     | appRoleMember（协作者） | [batchCreate](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role-member/batch_create)、[batchDelete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role-member/batch_delete)、[create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role-member/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role-member/delete)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/advanced-permission/app-role-member/list) |     |
|     | appTable（数据表） | [batchCreate](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/batch_create)、[batchDelete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/batch_delete)、[create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/delete)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/list)、[patch](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/patch) |     |
|     | appTableField（字段） | [create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/delete)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/list)、[update](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/update) |     |
|     | appTableFormField（表单项） | [list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/form/list)、[patch](https://open.feishu.cn/document/server-docs/docs/bitable-v1/form/patch) |     |
|     | appTableForm（表单） | [get](https://open.feishu.cn/document/server-docs/docs/bitable-v1/form/get)、[patch](https://open.feishu.cn/document/server-docs/docs/bitable-v1/form/patch-2) |     |
|     | appTableRecord（记录） | [batchCreate](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_create)、[batchDelete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_delete)、[batchUpdate](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/batch_update)、[create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/delete)、[get](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/get)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/list)、[update](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update) |     |
|     | appTableView（视图） | [create](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/create)、[delete](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/delete)、[get](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/get)、[list](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/list)、[patch](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/patch) |     |
| drive（云文档-文件管理） | media（素材） | [download](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/download)、[uploadAll](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/upload_all) |     |

  
同步自文档: https://feishu.feishu.cn/docx/RlrpdAGwnoONCaxmIVQcD7MZnug#HmqHdmIXbswu4xbNd9gc7oqDnUe

**完整示例**

**一、批量查找替换多行文本**

Python  
from baseopensdk import BaseClient  
from baseopensdk.api.base.v1 import \*  
from dotenv import load_dotenv, find_dotenv  
import os  
<br/>load_dotenv(find_dotenv())  
<br/>APP_TOKEN = os.environ\['APP_TOKEN'\]  
PERSONAL_BASE_TOKEN = os.environ\['PERSONAL_BASE_TOKEN'\]  
TABLE_ID = os.environ\['TABLE_ID'\]  
<br/>def search_and_replace(source: str, target: str):  
\# 1. 构建client  
client: BaseClient = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.build()  
<br/>\# 2. 获取当前表字段信息  
list_field_request = ListAppTableFieldRequest.builder() \\  
.page_size(100) \\  
.table_id(TABLE_ID) \\  
.build()  
<br/>list_field_response = client.base.v1.app_table_field.list(list_field_request)  
fields = getattr(list_field_response.data, 'items', \[\])  
<br/>\# 3. 取出文本字段  
text_field_names = \[field.field_name for field in fields if field.ui_type == 'Text'\]  
<br/>\# 4. 遍历记录  
list_record_request = ListAppTableRecordRequest.builder() \\  
.page_size(100) \\  
.table_id(TABLE_ID) \\  
.build()  
<br/>list_record_response = client.base.v1.app_table_record.list(list_record_request)  
records = getattr(list_record_response.data, 'items', \[\])  
<br/>records_need_update = \[\]  
<br/>for record in records:  
record_id, fields = record.record_id, record.fields  
new_fields = {}  
<br/>for key, value in fields.items():  
\# 替换多行文本字段的值  
if key in text_field_names:  
new_value = value.replace(source, target)  
\# 把需要替换的字段加入 new_fields  
new_fields\[key\] = new_value if new_value != value else value  
<br/>if len(new_fields.keys()) > 0:  
records_need_update.append({  
"record_id": record_id,  
"fields": new_fields  
})  
<br/>print(records_need_update)  
<br/>\# 5. 批量更新记录  
batch_update_records_request = BatchUpdateAppTableRecordRequest().builder() \\  
.table_id(TABLE_ID) \\  
.request_body(  
BatchUpdateAppTableRecordRequestBody.builder() \\  
.records(records_need_update) \\  
.build()  
) \\  
.build()  
batch_update_records_response = client.base.v1.app_table_record.batch_update(batch_update_records_request)  
print('success!')  
<br/><br/>if \__name__ == "\__main_\_":  
\# 替换所有文本字段中 'abc' 为 '233333'  
search_and_replace('abc', '233333')

**二、将链接字段对应的文件传到附件字段**

Python  
from baseopensdk import BaseClient  
from baseopensdk.api.base.v1 import \*  
from baseopensdk.api.drive.v1 import \*  
from dotenv import load_dotenv, find_dotenv  
import os  
import requests  
<br/>load_dotenv(find_dotenv())  
<br/>APP_TOKEN = os.environ\['APP_TOKEN'\]  
PERSONAL_BASE_TOKEN = os.environ\['PERSONAL_BASE_TOKEN'\]  
TABLE_ID = os.environ\['TABLE_ID'\]  
<br/>def url_to_attachment():  
\# 1. 构建client  
client: BaseClient = BaseClient.builder() \\  
.app_token(APP_TOKEN) \\  
.personal_base_token(PERSONAL_BASE_TOKEN) \\  
.build()  
<br/>\# 2. 遍历记录  
list_record_request = ListAppTableRecordRequest.builder() \\  
.page_size(100) \\  
.table_id(TABLE_ID) \\  
.build()  
<br/>list_record_response = client.base.v1.app_table_record.list(list_record_request)  
records = getattr(list_record_response.data, 'items', \[\])  
<br/>for record in records:  
record_id, fields = record.record_id, record.fields  
\# 3. 拿到链接字段值  
link = (fields.get('Link', {})).get('link')  
if link:  
\# 4. 下载图片  
image_resp = requests.get(link, stream=True)  
content = image_resp.content  
<br/>\# 5. 上传图片到 Drive 获取 file_token  
request = UploadAllMediaRequest.builder() \\  
.request_body(UploadAllMediaRequestBody.builder()  
.file_name('test.png')  
.parent_type("bitable_image")  
.parent_node(APP_TOKEN)  
.size(len(content))  
.file(content)  
.build()) \\  
.build()  
response = client.drive.v1.media.upload_all(request)  
<br/>file_token = response.data.file_token  
print(file_token)  
<br/>\# 6. 更新 file_token 到附件字段  
request = UpdateAppTableRecordRequest.builder() \\  
.table_id(TABLE_ID) \\  
.record_id(record_id) \\  
.request_body(AppTableRecord.builder()  
.fields({  
"Attachment": \[{"file_token": file_token}\] # 👆🏻前面接口返回的 file_token  
})  
.build()) \\  
.build()  
response: UpdateAppTableRecordResponse = client.base.v1.app_table_record.update(request)  
<br/><br/>if \__name__ == "\__main_\_":  
url_to_attachment()

**三、自动更新进度条**

[自动更新进度条](https://feishu.feishu.cn/docx/QhhwdXF8koFmeWxSagBccfKPnnd)

**在 Replit 上使用服务端 SDK**

我们提供了一个 [Replit 模板](https://replit.com/@lark-base/BaseOpenSDK-Python-Playground#main.py)，它使用 Flask 框架搭建了一个简单的服务器，监听了指定路径，当我们在 Base 上运行这个脚本，就会触发脚本函数的调用。

TypeScript  
from flask import Flask  
from playground.search_and_replace import search_and_replace_func  
<br/>app = Flask(\__name_\_)  
<br/>@app.route('/')  
def index():  
return 'Hello from Flask!'  
<br/>@app.route('/search_and_replace')  
def search_and_replace():  
search_and_replace_func('abc', '123')  
return 'success！！！'  
<br/><br/>app.run(host='0.0.0.0', port=81)  

上述代码监听/search_and_replace接口路径，并执我们的[示例一](https://feishu.feishu.cn/docx/AtcId8w25oAj4WxOaxicsXgGn8b#doxcnoNXBhMZxrItRGWfRT7cGNh)中定义的函数，实现操作 Base 数据

**方式一：在 Base Script 使用 Replit 链接触发脚本调用**

在 Replit 上 Fork [官方模板](https://replit.com/@lark-base/BaseOpenSDK-Python-Playground#main.py)

通过 Replit Secret 添加环境变量 APP_TOKEN、PERSONAL_BASE_TOKEN、TABLE_ID

点击 Run 起 Replit 服务

拷贝 replit 项目域名 + 接口路径，填入 Base Script，保存后点击运行即可触发服务端脚本

**\[Screen Recording 2023-07-12 at 16.27.04.mov\]**

**方式二：Replit 服务端直接运行脚本**

如果你的项目无需手动触发，可以直接在 Replit 控制台运行脚本

Shell  
python ./playground/search_and_replace.py