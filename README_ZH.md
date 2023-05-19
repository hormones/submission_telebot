# 一个简单的用于频道投稿的Telegram机器人

**简体中文 | [English](./README.md) | [日本語](./README_JP.md)**<br>

## 功能
- [x] 支持匿名发布稿件，支持发送文本、图片、视频等
- [x] 审核完成后，审核人员可回复用户被拒绝或通过的原因
- [x] 多语言，目前支持中文、英文和日语
- [x] 管理员可查看/封禁/解封用户
- [x] 管理员可直接在BOT中查看/修改部分配置
- [x] 不允许匿名投稿转发的消息
- [x] 用户通过`/feedback`指令反馈问题

## 待实现功能
- [ ] 投稿内容限制，如限制字数、图片数量等
- [ ] 投稿统计
- [ ] 通过BOT在投稿评论中发言（匿名时十分有用）
- [ ] 支持DOCKER部署

## 说明
1. 有哪几种角色？

    管理员：BOT管理员，可以查看/修改部分配置，查看/封禁/解封用户

    审核员：可以审核投稿

    普通用户：可以使用BOT投稿

2. 如何添加管理员
    服务启动前，在`config.yml`中的`super_admins`属性中配置，多个管理员用英文逗号`,`分隔
3. 如何添加审核员
    邀请审核员加入审核频道即可，订阅了审核频道的用户均可审核投稿
4. 如何设置默认语言
    在`i18n.yml`中的`langs`属性中配置，将默认语言放在第一位

## 准备
1. 在 https://my.telegram.org/apps 这里申请api_id和api_hash
2. 在 [@botfather](https://t.me/botfather) 处申请一个BOT的Token
3. 准备一个审核频道，必须是私有频道，将机器人加入频道并赋予管理员权限
4. 准备一个审核群组，必须是私有群组，并链接到审核频道，将机器人加入群组并赋予管理员权限
5. 准备一个展示频道，将机器人加入频道并赋予管理员权限，审核通过的投稿将会被转发到此频道
6. 通过 [@userinfobot](https://t.me/userinfobot) 获取以上频道和群组的ID

## 部署

首次运行此BOT服务需要执行1、2、3步，后续运行直接执行第3步即可

1. 在服务器上执行下列命令（请先安装git，python >= 3.7.3）
```bash
git clone https://github.com/hormones/submission_telebot
cd submission_telebot
python3 -m venv venv
source ./venv/bin/activate
pip install -U pip setuptools
pip install -r requirements.txt
```
2. 修改 `config.yml` 文件（或者配置环境变量），认真阅读注释并填入正确的配置
3. 运行 `source ./venv/bin/activate && nohup python main.py >/dev/null 2>&1 &` 启动服务


## 指令

用户默认可用指令有`/help`、`/lang`、`/feedback`，可修改配置文件中的 `user_command` 来添加或删除用户可用指令

BOT管理员默认可使用所有指令，不可配置修改

| 命令      | 参数                        | 默认权限范围         | 使用范围                 | 说明                                             |
| --------- | --------------------------- | -------------------- | ------------------------ | ------------------------------------------------ |
| /help     | 可选，命令名称              | 所有人均可使用       | BOT中可用                | 查看帮助，可输入命令参数查看对应命令详细使用方法 |
| /setting  | -                           | BOT管理员可用        | BOT中可用                | 查看/修改部分设置                                |
| /ban      | 可选，用户ID/用户名/@用户名 | BOT管理员可用        | BOT中可用                | 查看/封禁/解封用户                               |
| /lang     | -                           | 所有人均可使用       | BOT中可用                | 多语言                                           |
| /feedback | 必填，反馈内容              | 普通用户可用         | BOT中可用                | 反馈问题                                         |
| /reply    | 必填，回复内容              | 审核频道所有成员可用 | 审核频道消息内评论时可用 | 审核完成后，回复用户被拒绝或通过的原因           |

## 使用开源协议
MIT

## 示例
[@submission_telebot](https://t.me/submission_telebot)

## 目前存在的问题/优化点
- [ ] 桌面版本在一条消息中投稿多张图片时，如果选择不压缩图片，会被Telegram依次发送，导致投稿被切分成多条消息（压缩图片则没有这个问题，暂时没有好的解决方案）

## 其它
1. 如果启动异常，请先查看日志文件 `submission_telebot.log`排查问题，如有问题请提交issue
1. `config.yml` 文件中的配置均可以配置为系统环境变量，当存在对应配置的环境变量时，将会覆盖配置文件中的配置
1. 本项目中英语和日语翻译均来自[Github Copilot](https://github.com/features/copilot)插件翻译，如有不妥之处请提交issue
1. 如果有定制化信息展示的需要，可以自行研究编辑 `i18n.yml` 文件中的多语言配置，以更加贴合项目主题
1. 如有其它问题或建议，欢迎提交issue