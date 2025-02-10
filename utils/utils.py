import copy
import json

import requests
from constants import HEADERS, API_URL, PAYLOAD


def get_news_info(user_content):
    payload = copy.deepcopy(PAYLOAD)

    payload['messages'].append(
        {
            "role": "user",
            "content": user_content
        }
    )
    response = requests.request("POST", API_URL, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return {}
    result = response.json()
    choices = result.get('choices')
    for choice in choices:
        content = choice.get('message').get('content').replace('```json', '').replace('```', '').strip()
        json_content = json.loads(content)
        return json_content


if __name__ == '__main__':
    user_content = """日前，中国人民银行、商务部、金融监管总局、中国证监会、国家外汇局五部门联合印发《关于金融领域在有条件的自由贸易试验区（港）试点对接国际高标准推进制度型开放的意见》（以下简称《意见》），进一步推动在天津自贸试验区等试点金融领域制度型开放。

　　《意见》聚焦6个方面：

　　允许外资金融机构开展与中资金融机构同类新金融服务。新金融服务的开展遵循内外一致原则，除涉及国家安全、金融安全等因素的特定新金融服务外，如允许中资金融机构开展，则应允许试点地区外资金融机构开展。

　　120天内就金融机构开展相关服务的申请作出决定。按照内外一致原则，对境外金融机构、境外金融机构的投资者、跨境金融业务提供者提交的在试点地区开展金融服务相关的完整且符合法定形式的申请，自受理之日起120天内作出决定，并及时通知申请人。如不能在120天内作出决定，应及时与申请人沟通解释。

　　支持依法跨境购买一定种类的境外金融服务。其中包括：在真实合规的前提下，试点地区企业和个人可依法办理经常项下跨境保单的续费、理赔、退保等跨境资金结算；在粤港澳大湾区持续优化“跨境理财通”试点，支持粤港澳大湾区内地居民通过港澳金融机构购买港澳金融机构销售的合资格投资产品。扩大参与机构范围和合资格投资产品范围等。

　　便利外国投资者投资相关的转移汇入汇出。在真实合规的前提下，允许试点地区真实合规的、与外国投资者投资相关的所有转移可自由汇入、汇出且无迟延等。

　　最后两个方面分别是完善金融数据跨境流动安排，以及全面加强金融监管、有效防范化解金融风险。

　　根据《意见》，上述政策措施在上海、广东、天津、福建、北京自由贸易试验区和海南自由贸易港等地区，以及党中央、国务院作出明确部署承担对外开放重要任务的合作平台先行先试，推动试点地区在更广领域、更深层次开展探索，实现自由贸易试验区（港）制度型开放、系统性改革成效、开放型经济质量的全面提升。"""

    result = get_news_info(user_content)
    print(result)
