# Docx2KG

## 环境设置

1、python环境

本项目python环境并不复杂，但是我在期初一直在做各种文档处理的尝试，导致环境比较复杂，因此我不建议你直接安装requirements

你可以用你做文档切分的那个环境

再额外安装以下包：

```shell
pip install XMind
pip install dashscope
pip install fitz
pip install signal
pip install nltk
pip install python-docx
```

版本并不影响使用

其中在dashscope中，我不太清楚最新版的包是否更正了缺少max以及longcontent模型的问题

如果没有，你可以在其Generation类中的Models类添加配置

参考示例如下

```python
class Generation(BaseApi):
    task = 'text-generation'
    """API for AI-Generated Content(AIGC) models.

    """
    class Models:
        """@deprecated, use qwen_turbo instead"""
        qwen_v1 = 'qwen-v1'
        """@deprecated, use qwen_plus instead"""
        qwen_plus_v1 = 'qwen-plus-v1'

        bailian_v1 = 'bailian-v1'
        dolly_12b_v2 = 'dolly-12b-v2'
        qwen_turbo = 'qwen-turbo'
        qwen_plus = 'qwen-plus'
        qwen_max = 'qwen-max'
        qwen_max_longcontext ='qwen-max-longcontext'
```

## 项目代码与功能

**main.ipynb**: 主要代码，稍后分步介绍；

**build.ipynb**: 从main中剥离出来涉及到思维导图构建的代码

**buildKG/docx2request.py** : 承担源文件转text以及限制发送请求的文段长短的工作

​	count_tokens：统计tokens数量（不准）

​	read_paragraphs：从docx中读取段落（后续docx转pdf做，接口不用了）

​	group_paragraphs_by_token_limit：对docx的文段，限制文段长度，将一个文段按照tokens限制拆成多个文段（后续用pdf了，接口不用了）

​	extract_text_from_pages：按页提取pdf的文字内容并整理成一个文段

​		输入：路径，起始页，终止页

​		输出：文段

​	group_page_by_token_limit：限制文段长度，将一个文段按照tokens限制拆成多个文段（后续统一用小节作为长度单位，还在用，但并不体现作用）

**buildKG/str2json.py**：

​	str2json:对小节知识点提取过程中大模型返回值进行分析，返回节点列表和边列表

​	indexstr2json：对目录提取过程中大模型返回值进行分析，返回值具体参考main.ipynb中注解

**buildKG/forest.py**:

​	handler: 超时终止

​	Node 类：表征知识点

​	Edge 类: 表征知识点之间的关系

​		注：由于xmind底层接口的不稳定性，因此我们将边的构造单独拆出来做为一个函数，以防构建失败or超时

​	Forest 类：表征排除根节点之后，整个思维导图

​		除增加节点、增加边、构建森林 、打印节点之外

​		get_tree_roots：获取无根节点的节点

​		build_kg：构建图谱

## 如何使用？

由于大模型构建的不稳定性，我们不得不引入人在循环当中，此时ipynb就相较于单个py文件更有性价比。

在我们的main中，我们将构建工作分为5步：1、数据预处理；2、切分文段；3、输入大模型；4、反馈整合输出；5、分步重构；

下文按照上述步骤介绍各部分功能及用法：

### 1、数据预处理

功能：引入必要库；处理原始文件；

用法：由于数据有很多类型（图片型pdf、docx、分段的docx、没有目录的docx）我的建议是这一步手做，将源文件整理成有目录的docx然后用wps或word转成能提取文字的pdf，相较于其他方案要快很多也稳定一些；后续如果只有图片型pdf会增加ocr组件去做文字提取。

### 2、文段切分

功能：提取目录，给到最简单的知识框架

由于各个书的结构不一致，有的书前言可能在目录之前有较多的页数，因此我们采取手动分页的方式

简单使用：依次执行、观察大模型提取结果是否符合要求；并保存相关结果；

复杂情况：目录页数较多或者条目较多要分批次处理，可以手动划分一下，然后观察每一轮的输入输出；按照大模型输出——数据保存——清空——大模型输出——数据读取+合并的思路来做；应该能用循环重写，因为这种情况比较特殊我就遇到过一次，而且中间有时容易失败所以我是分批做的；

### 3、输入提示词设计

直接点吧？prompt能优化空间还蛮大的；

### 4、反馈整合，xmind输出

直接点；点之前先点一下下面的分布重构中的输出信息保存；

### 5、分布重构

就是把debug里面收集到的再重跑一下；主要应对输出格式不正确添加了解释或者其他情况，但是很麻烦的问题是大多数重构依然会失败；或许可以调一下提示词

## 改进空间

1、目前是通过两两知识点不一样，这样一个假设去做的构建体系，容易出现bug；

2、构建关系容易出现超时或失败问题，bug难de，从表层也没有找到直观的原因；

3、输出有时会出现解释or不以json形式输出；

4、现阶段我尽可能控制它只输出一种属于关系，但是也会有其他关系输出；

5、大模型提取到的结果，野节点（与其他节点没有关系的节点）很多；提取效果不是很理想；

## 下一步规划

1、COT链路优化改进prompt，优化提取效果，以及输出效果

2、将生成的例子加入prompt，尝试过将生成的内容加入prompt，但是似乎生成文本会很长、量会很少、且会造成一定的输出格式污染，或许可以通过cot进行改进？

3、改进构建体系流程，修复bug

4、沿着COT的思路，如何更好的提取文段中的知识点

5、拓宽任务场景，在LLM代码生成中思考本项目中遇到的问题

