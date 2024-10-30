# Academic Agents V2 (学术写作智能助手)

Academic Agents V2 是一个基于大语言模型的学术论文写作辅助工具。它通过多个专业化的智能代理（Agents）来协助用户完成从选题到大纲的论文写作过程。

## 功能特点

- 🎯 **研究领域确定**：根据用户的专业背景和学术兴趣，推荐合适的研究领域
- 🔍 **研究对象分析**：提供3-5个具体的研究对象建议
- 💡 **本质问题提炼**：帮助分析现象问题，揭示深层本质问题
- 📝 **研究论题形成**：协助构建理论框架，形成完整研究论题
- 📑 **论文框架生成**：自动生成论文题目和详细的三级目录结构

## 安装要求

- Python 3.8+
- 依赖包：

  ```bash
  pip install -r requirements.txt
  ```

## 配置说明

本项目支持两种配置方式：

1. 环境变量配置
2. .env 文件配置

### 配置项

```bash
YI_API_KEY=your_api_key_here
YI_BASE_URL=<https://api.lingyiwanwu.com/v1>
YI_MODEL=yi-large
```

请复制 `.env.example` 文件为 `.env` 并填入你的配置信息。

## 使用方法

1. 克隆项目：

   ```bash
   git clone https://github.com/anarchysaiko/academicagentsV2.git
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量或 .env 文件

4. 运行程序：

   ```bash
   python app.py
   ```

5. 按照提示输入你的专业领域和学术兴趣

## 输出说明

程序会生成一个 Markdown 格式的输出文件，包含：

- 论文题目
- 详细的三级目录结构
- 完整的研究过程记录

输出文件命名格式：`research_process_YYYYMMDD_HHMMSS.md`

## 代理（Agents）说明

本项目包含以下专业化代理：

- **ResearchField**: 研究领域专家
- **ResearchObject**: 研究对象定义专家
- **EssentialProblem**: 研究问题分析专家
- **ResearchThesis**: 研究论题专家
- **PaperTitleAndOutline**: 论文题目和大纲专家

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 联系方式

如有问题或建议，请通过 GitHub Issues 与我们联系。
