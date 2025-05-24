#!/bin/bash

while true; do
    # 提示用户输入提交信息
    echo "请输入提交信息（例如：[add]新增 axios 配置）："
    read COMMIT_MESSAGE

    # 检查提交信息是否为空
    if [ -z "$COMMIT_MESSAGE" ]; then
        echo "错误: 提交信息不能为空"
        continue
    fi

    # 显示用户输入的提交信息并确认
    echo "您的提交信息是: \"$COMMIT_MESSAGE\""
    echo "这个提交信息正确吗? (y/n)"
    read CONFIRM

    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        break
    else
        echo "请重新输入提交信息。"
    fi
done

# 执行git命令
echo "执行: git add ."
git add .

# 使用单引号包裹双引号，以确保完整传递提交信息
echo "执行: git commit -m \"$COMMIT_MESSAGE\""
git commit -m "$COMMIT_MESSAGE"

# 检查commit结果
if [ $? -ne 0 ]; then
    echo "提交失败。"
    exit 1
fi

echo "执行: git push origin HEAD:main"
git push origin HEAD:main

# 检查push结果
if [ $? -eq 0 ]; then
    echo "推送成功!"
else
    echo "推送失败。网络问题，请稍后重试。"
fi