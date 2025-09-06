# 在这里，您可以通过 'args'  获取节点中的输入变量，并通过 'ret' 输出结果
# 'args' 已经被正确地注入到环境中
# 下面是一个示例，首先获取节点的全部输入参数params，其次获取其中参数名为'input'的值：
# params = args.params; 
# input = params['input'];
# 下面是一个示例，输出一个包含多种数据类型的 'ret' 对象：
# ret: Output =  { "name": '小明', "hobbies": ["看书", "旅游"] };
import json

async def main(args: Args) -> Output:
    detail = args.params["detail"]
    finalStatus = args.params["finalStatus"]
    finalStatusDesc = args.params["finalStatusDesc"]
    input = args.params["input"]
    shentong = args.params["shentong"]
    status_mapping = {
        "got": "已揽收",
        "transit": "运输中",
        "deliver": "派送中",
        "inStore": "已到店",
        "signed": "已签收"
    }
    if shentong:
        # shentong数据处理逻辑
        state_mapping = {
            "0": "在途",
            "1": "揽收",
            "2": "疑难",
            "3": "签收",
            "4": "退签",
            "5": "派件",
            "8": "清关",
            "14": "拒签"
        }
        shentong_data = json.loads(shentong)
        state = str(shentong_data.get("state", "0"))
        finalStatus = state_mapping.get(state, "在途")
        finalStatusDesc = shentong_data["data"][0]["context"]
        detail = shentong_data["data"]
    else:
        # 现有逻辑
        if not finalStatus:
            # 如果detail列表不为空
            if detail:
                # 获取detail列表的最后一项
                last_detail = detail[-1]
                # 更新finalStatus和finalStatusDesc
                finalStatus = last_detail.get("status", "")
                
                finalStatus = status_mapping.get(finalStatus, finalStatus)
                finalStatusDesc = status_mapping.get(finalStatus, finalStatus)
    

    ret = {
        "finalStatus": finalStatus,
        "finalStatusDesc": finalStatusDesc,
        "statusDetail": detail,
    }

    return ret