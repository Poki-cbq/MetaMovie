/**
 * 组件测试公共 fixture 文件
 * 可用于挂载任意组件时注入插件、mock 等
 */
import { config } from "@vue/test-utils";
import ElementPlus from "element-plus";

// 全局注册 Element Plus（mock 组件测试中需要）
config.global.plugins = config.global.plugins || [];

// 重置所有 mock（在 afterEach 中调用）
export function resetAllMocks() {
  vi.clearAllMocks();
}
