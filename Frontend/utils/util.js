// 定义一个函数 formatTime，接收一个 Date 对象作为参数
const formatTime = date => {
  // 获取年份
  const year = date.getFullYear()
  // 获取月份（注意：getMonth() 返回值从 0 开始，所以需要加 1）
  const month = date.getMonth() + 1
  // 获取日期
  const day = date.getDate()
  // 获取小时
  const hour = date.getHours()
  // 获取分钟
  const minute = date.getMinutes()
  // 获取秒数
  const second = date.getSeconds()

  // 将年、月、日和时、分、秒分别格式化后拼接成字符串返回
  // 使用 map 调用 formatNumber 函数确保每个数字至少两位数
  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

// 定义辅助函数 formatNumber，用于将单位数补前导零
const formatNumber = n => {
  // 将数值转换为字符串
  n = n.toString()
  // 如果是个位数，则前面补 '0'；否则直接返回原字符串
  return n[1] ? n : `0${n}`
}

// 导出 formatTime 函数供其他模块使用
module.exports = {
  formatTime
}