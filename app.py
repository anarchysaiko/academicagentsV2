import os
from dotenv import load_dotenv
import autogen
from openai import AuthenticationError as openai_AuthenticationError
from colorama import Fore, Back, Style, init
import datetime

# 初始化 colorama
init(autoreset=True)

# 加载 .env 文件
load_dotenv()


def get_config():
    """获取API配置，优先使用环境变量，其次使用.env文件"""
    # 尝试从环境变量获取配置
    api_key = os.getenv("YI_API_KEY")
    base_url = os.getenv("YI_BASE_URL")
    model = os.getenv("YI_MODEL", "yi-large")  # 设置默认值为 yi-large

    if not api_key or not base_url:
        print(
            Fore.RED
            + "警告: 未找到API配置。请确保设置了环境变量或.env文件。"
            + Style.RESET_ALL
        )
        print("需要设置以下环境变量:")
        print("- YI_API_KEY: API密钥")
        print("- YI_BASE_URL: API基础URL")
        print("- YI_MODEL: 模型名称（可选，默认为yi-large）")
        exit(1)

    return [
        {
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
        }
    ]


# 替换原有的 config_list
config_list = get_config()


def get_human_input():
    user_input = input(
        Fore.YELLOW + "您的回复 (输入 'exit' 切换到下一个 agent): " + Style.RESET_ALL
    )
    return user_input if user_input.lower() != "exit" else None


def run_conversation(agent, user_proxy, initial_message, context=""):
    print(Fore.CYAN + f"\n--- 开始与 {agent.name} 的对话 ---" + Style.RESET_ALL)
    print(Fore.MAGENTA + "上下文:" + Style.RESET_ALL)
    print(context)
    print(Fore.MAGENTA + "初始消息:" + Style.RESET_ALL)
    print(initial_message)

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": initial_message},
    ]
    response = agent.generate_reply(sender=user_proxy, messages=messages)
    print(Fore.GREEN + f"{agent.name}: {response}" + Style.RESET_ALL)

    full_conversation = f"{context}\n\n{agent.name}: {response}"

    while True:
        user_input = get_human_input()
        if user_input is None:
            break
        messages.append({"role": "user", "content": user_input})
        response = agent.generate_reply(sender=user_proxy, messages=messages)
        print(Fore.GREEN + f"{agent.name}: {response}" + Style.RESET_ALL)
        full_conversation += f"\n\nHuman: {user_input}\n\n{agent.name}: {response}"

    print(Fore.CYAN + f"--- 结束与 {agent.name} 的对话 ---\n" + Style.RESET_ALL)
    return full_conversation


# 创建agents
user_proxy = autogen.UserProxyAgent(
    name="Human",
    system_message="""你是一个人文社会科学研究者，需要协助完成论文选题和写作。在这个过程中，请遵循以下原则：

1. 坚持专业方向：
   - 确保论文选题聚焦于你的专业领域（例如，公共管理学科领域）

2. 理论联系实际：
   - 选题应该既有理论基础，又能解决实际问题

3. 聚焦实践问题：
   - 选题要密切结合研究领域的理论实践问题
   - 关注当前热点和实际需求

4. 明确研究对象：
   - 选题要落实到研究领域的具体领域和具体问题
   - 避免过于宽泛或模糊的主题

5. 创新性：
   - 选题要有新观点、新见解
   - 确保选题具有理论和应用价值

6. 可行性：
   - 考虑研究的可行性，包括时间、资源等因素
   - 评估资料获取的难易程度

你的任务是在整个论文选题和写作过程中，根据这些原则提供指导和反馈。请确保每个步骤都符合这些原则，并在必要时提出修改建议。""",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

research_field = autogen.ConversableAgent(
    name="ResearchField",
    system_message="""你是一个专业的研究领域专家。你的任务是根据用户的专业背景和学术兴趣，确定一个具体且有价值的研究领域。请遵循以下步骤：

1. 分析用户的专业背景（大前提条件）：
   - 确保研究领域与用户的专业背景紧密相关
   - 例如，公共管理专业的用户应围绕公共管理领域，如行政管理、现代城市社会治理等

2. 考虑用户的学术兴趣（小前提条件）：
   - 将用户的兴趣与其专业背景结合
   - 例如，对生成式人工智能感兴趣的公共管理专业用户，可以研究生成式人工智能在公共管理领域的应用和影响

3. 提出创新视角：
   - 尝试新的角度解释传统问题
   - 或探索专业领域中新兴的研究方向

4. 考虑当前的学术热点和发展趋势

5. 提出2-3个可能的研究领域选项，并解释每个选项的以下方面：
   - 与用户专业背景的相关性
   - 如何结合用户的学术兴趣
   - 研究的创新性
   - 潜在的学术价值和实际应用价值

请确保你的建议既符合用户的专业背景，又能满足其学术兴趣，同时具有学术价值和创新性。""",
    llm_config={"config_list": config_list},
)

research_object = autogen.ConversableAgent(
    name="ResearchObject",
    system_message="""你是一个研究对象定义专家。基于已确定的研究领域，你的任务是提出3-5个具体的研究对象。在确定研究对象时，请遵循以下原则：

1. 具体明确：
   - 研究对象应该比研领域更加具体和明确
   - 例如，如果研究领域是"民营养老"，那么研究对象可以是"民营养老机构的定价机制"

2. 问题导向：
   - 研究对象应该包含可以解释的问题或社会热点问题
   - 确保选择的研究对象能够引发有意义的学术讨论或解决实际问题

3. 可行性：
   - 研究对象应该具有研究的可行性
   - 可以进行实证调研或获得相关统计数据
   - 考虑数据可获得性和研究方法的适用性

对于每个提出的研究对象，请提供以下信息：
1. 研究对象的具体描述
2. 与该研究对象相关的潜在问题或社会热点
3. 研究该对象的可行性分析（如可能的数据来源、研究方法等）
4. 该研究对象的理论意义和实际应用价值

请确保你提出的研究对象既符合上述原则，又与之前确定的研究领域紧密相关。""",
    llm_config={"config_list": config_list},
)

essential_problem = autogen.ConversableAgent(
    name="EssentialProblem",
    system_message="""你是一个研究问题分析专家。你的任务是深入分析研究对象，揭示其中的本质问题。请遵循以下步骤：

1. 识别现象问题：描述具体的、多变的社会矛盾现象或难以解释的社会现象。

2. 分析深层原因：通过"果索因"的方法，探究导致现象问题的根本原因。考虑社会经济因素、制度因素、文化因素等多个方面。

3. 提炼本质问题：
   - 找出决定现象问题背后的内在矛盾
   - 确保本质问题是看不见的、不变的，且能解释多个现象问题
   - 使用简洁、明确的名词性结构表述
   - 避免"假问题"，确保提出的是"真问题"

4. 展示推理过程：清晰地说明从现象问题到本质问题的推理过程。

5. 最终输出：
   - 现象问题：[简要描述]
   - 推理过程：[详细说明]
   - 本质问题：[使用名词性结构，不超过10个字]

请确保你的分析逻辑清晰，论证有力，并能揭示问题的本质。""",
    llm_config={"config_list": config_list},
)

research_thesis = autogen.ConversableAgent(
    name="ResearchThesis",
    system_message="""你是一个研究论题专家。你的任务是基于之前的讨论，形成一个完整的研究论题。研究论题是对解决本质问题的基本判断，也可以说是基本理论假设。在形成研究论题时，请遵循以下步骤：

1. 理论假设的提出：
   - 根据研究问题的性质，选择合适的理论作为研究的基础
   - 确保选择的理论与之前讨论的研究对象和本质问题相关

2. 构建理论框架：
   - 阐述所选理论的核心概念、主要观点、假设前提以及发展历程
   - 分析理论对于当前研究问题的适应性
   - 根据理论框架，进一步明确研究问题和研究目标

3. 形成完整的研究论题：
   - 对本质问题提出基本判断
   - 阐述初步的理论框架
   - 提出具体的研究问题
   - 明确研究目标

请确保你的研究论题：
1. 与之前讨论的研究对象和本问题紧密相关
2. 具有理论深度和现实意义
3. 能够在所选理论框架的指导下得到深入探讨
4. 清晰、具体，并能引导后续的研究过程

请提供一个结构化的研究论题，包括上述所有要素。""",
    llm_config={"config_list": config_list},
)

paper_title = autogen.ConversableAgent(
    name="PaperTitleAndOutline",
    system_message="""你是一个论文题目和大纲专家。你的任务是基于之前的所有讨论，创造一个引人注目且学术性强的论���题目，并生成详细的三级目录。请遵循以下步骤：

1. 凝练论文题目：
   a) 内容完整性：包含研究对象和研究问题
   b) 简洁明了：控制在20个字以内
   c) 学术性：使用恰当的学术用语
   d) 吸引力：突出研究的创新性或重要性

2. 生成三级目录：
   a) 严格遵循提供的目录结构框架
   b) 每一章的标题、每一节的标题、每一目的标题都使用名词性结构，不使用逗号分隔
   c) 确保章标题、节标题与目标题之间形成逻辑闭环
   d) 第3章到第7章的具体内容需要根据研究内容进行扩展

3. 目录结构说明：
   第1章 绪论
   1.1 研究缘起（强调论文写作背景和研究问题，结合研究内容高度凝练）
   1.1.1 研究背景
   1.1.2 研究问题
   1.2 研究意义（解释解决研究问题的意义，结合研究内容）
   1.2.1 理论意义
   1.2.2 实践意义
   1.3 国内外研究现状（文献综述，包括实践发展、不足、政策与实施状况）
   1.3.1 国内研究现状
   1.3.2 国外研究现状
   1.4 研究方法（至少两个研究方法，说明方法是什么，为什么使用，如何使用）
   1.4.1 研究方法1
   1.4.2 研究方法2
   1.5 研究思路（研究角度、展开方面、技术路线）
   1.5.1 研究角度
   1.5.2 研究框架结构

   第2章 核心概念与理论基础
   2.1 核心概念（不超过3个，阐释包括提出者、普遍观点、不同观点）
   2.1.1 核心概念1
   2.1.2 核心概念2
   2.1.3 核心概念3
   2.2 理论基础（不超过2个理论，说明选择原因、依据和应用方式）
   2.2.1 理论1
   2.2.2 理论2

   第3章 理论假设（针对研究问题，结合第2章理论基础提出假设）

   第4章 现实分析（通过实证调查方法揭示并分析问题）

   第5章 实证论证（通过定量分析模型论证之前提出的理论假设）

   第6章 实现路径（基于理论假设与论证结果，提出解决研究问题的实践路径）

   第7章 对策建议（提出实现理论假设和实践方案的对策建议）

请提供：
1. 一个符合要求的论文题目
2. 一个完整的三级目录，确保严格符合上述结构要求

确保你的题目和目录既符合学术规范，又能准确反映研究内容，同时具有吸引读者的能力。对于第3章到第7章，请根据之前的讨论内容进行适当扩展，保持逻辑一致性。""",
    llm_config={"config_list": config_list},
)

# 主程序
print(Fore.YELLOW + "请输入您的专业领域和学术兴趣:" + Style.RESET_ALL)
user_input = input()
initial_message = (
    f"用户的专业领域和学术兴趣是: {user_input}。请基于这些信息确定合适的研究领域。"
)

print(Fore.CYAN + "\n--- 开始论文写作过程 ---" + Style.RESET_ALL)

all_conversations = []

print(Fore.BLUE + "\n确定研究领域:" + Style.RESET_ALL)
field_context = run_conversation(research_field, user_proxy, initial_message)
all_conversations.append(("确定研究领域", field_context))

print(Fore.BLUE + "\n确定研究对象:" + Style.RESET_ALL)
object_context = run_conversation(
    research_object, user_proxy, "基于研究领域，请确定具体的研究对象。", field_context
)
all_conversations.append(("确定研究对象", object_context))

print(Fore.BLUE + "\n揭示本质问题:" + Style.RESET_ALL)
problem_context = run_conversation(
    essential_problem,
    user_proxy,
    "请基于之前的讨论，分析现象问题,找出本质问题。",
    object_context,
)
all_conversations.append(("揭示本质问题", problem_context))

print(Fore.BLUE + "\n形成研究的论题:" + Style.RESET_ALL)
thesis_context = run_conversation(
    research_thesis,
    user_proxy,
    "请基于之前的所有讨论，形成研究论题，并阐述理论框架。",
    problem_context,
)
all_conversations.append(("形成研究的论题", thesis_context))

print(Fore.BLUE + "\n凝练论文题目:" + Style.RESET_ALL)
title_context = run_conversation(
    paper_title,
    user_proxy,
    "请基于之前的所有讨论，凝练简洁明了的论文题目，并按照上述要求输出三级目录。",
    thesis_context,
)
all_conversations.append(("凝练论文题目", title_context))

print(Fore.CYAN + "\n--- 论文写作过程结束 ---" + Style.RESET_ALL)

# 将所有对话内容输出到 Markdown 文件
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"research_process_{timestamp}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write("# 研究过程记录\n\n")
    f.write(f"用户输入: {user_input}\n\n")

    # 只写入"凝练论文题目"的内容
    for title, content in all_conversations:
        if title == "凝练论文题目":
            f.write(f"## {title}\n\n")
            f.write(f"\n{content}\n\n")

print(Fore.GREEN + f"\n所有对话内容已保存到 {filename}" + Style.RESET_ALL)
