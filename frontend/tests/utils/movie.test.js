/**
 * 前端工具函数测试 — getPosterUrl / toStarRating / formatRuntime / getProfileUrl / formatMoney
 */
import { describe, it, expect } from "vitest";
import {
  getPosterUrl,
  toStarRating,
  formatRuntime,
  getProfileUrl,
  formatMoney,
} from "../../src/utils/movie";

// ===========================================================================
// getPosterUrl
// ===========================================================================
describe("getPosterUrl", () => {
  it("空路径返回空字符串", () => {
    expect(getPosterUrl("")).toBe("");
    expect(getPosterUrl(null)).toBe("");
    expect(getPosterUrl(undefined)).toBe("");
  });

  it("TMDB 路径拼接 CDN URL", () => {
    const result = getPosterUrl("/abc123.jpg", "tmdb", "w500");
    expect(result).toBe("https://image.tmdb.org/t/p/w500/abc123.jpg");
  });

  it("默认尺寸为 w500", () => {
    const result = getPosterUrl("/poster.jpg", "tmdb");
    expect(result).toContain("/w500/");
  });

  it("可指定其他尺寸", () => {
    const result = getPosterUrl("/poster.jpg", "tmdb", "w185");
    expect(result).toBe("https://image.tmdb.org/t/p/w185/poster.jpg");
  });

  it("豆瓣完整 URL 直接返回", () => {
    const doubanUrl = "https://img1.doubanio.com/view/photo/xxx.jpg";
    const result = getPosterUrl(doubanUrl, "douban");
    expect(result).toBe(doubanUrl);
  });

  it("豆瓣 HTTP 开头的任意 URL 直接返回", () => {
    const url = "http://example.com/img.jpg";
    const result = getPosterUrl(url, "douban");
    expect(result).toBe(url);
  });
});

// ===========================================================================
// toStarRating
// ===========================================================================
describe("toStarRating", () => {
  it("10 分满分 → 5 星", () => {
    expect(toStarRating(10)).toBe(5);
  });

  it("8.4 分 → 4.2 星", () => {
    expect(toStarRating(8.4)).toBe(4.2);
  });

  it("7.5 分 → 3.75 星", () => {
    expect(toStarRating(7.5)).toBe(3.75);
  });

  it("0 分 → 0 星", () => {
    expect(toStarRating(0)).toBe(0);
  });

  it("falsy 值返回 0", () => {
    expect(toStarRating(null)).toBe(0);
    expect(toStarRating(undefined)).toBe(0);
    expect(toStarRating("")).toBe(0);
  });

  it("负数评分按公式计算（虽然实际不会出现）", () => {
    expect(toStarRating(-2)).toBe(-1);
  });
});

// ===========================================================================
// formatRuntime
// ===========================================================================
describe("formatRuntime", () => {
  it("falsy 值返回空字符串", () => {
    expect(formatRuntime(0)).toBe("");
    expect(formatRuntime(null)).toBe("");
    expect(formatRuntime(undefined)).toBe("");
  });

  it("纯分钟不足一小时", () => {
    expect(formatRuntime(45)).toBe("45min");
  });

  it("整小时", () => {
    expect(formatRuntime(120)).toBe("2h 0min");
  });

  it("小时 + 分钟", () => {
    expect(formatRuntime(139)).toBe("2h 19min");
  });

  it("1 小时", () => {
    expect(formatRuntime(60)).toBe("1h 0min");
  });

  it("0 分钟", () => {
    expect(formatRuntime(0)).toBe("");
  });
});

// ===========================================================================
// getProfileUrl
// ===========================================================================
describe("getProfileUrl", () => {
  it("空路径返回空字符串", () => {
    expect(getProfileUrl("")).toBe("");
    expect(getProfileUrl(null)).toBe("");
  });

  it("默认尺寸为 w92", () => {
    const result = getProfileUrl("/profile.jpg");
    expect(result).toContain("/w92/");
  });

  it("拼接 TMDB CDN URL", () => {
    const result = getProfileUrl("/avatar.jpg", "w185");
    expect(result).toBe("https://image.tmdb.org/t/p/w185/avatar.jpg");
  });
});

// ===========================================================================
// formatMoney
// ===========================================================================
describe("formatMoney", () => {
  it("falsy 值返回 —", () => {
    expect(formatMoney(0)).toBe("—");
    expect(formatMoney(null)).toBe("—");
    expect(formatMoney(undefined)).toBe("—");
  });

  it("十亿以上 → B", () => {
    expect(formatMoney(1_500_000_000)).toBe("$1.5B");
  });

  it("百万以上 → M", () => {
    expect(formatMoney(2_800_000)).toBe("$3M");
  });

  it("百万以下 → 千分位", () => {
    expect(formatMoney(500_000)).toBe("$500,000");
  });

  it("刚好 1B", () => {
    expect(formatMoney(1_000_000_000)).toBe("$1.0B");
  });

  it("刚好 1M", () => {
    expect(formatMoney(1_000_000)).toBe("$1M");
  });

  it("小金额带千分位", () => {
    expect(formatMoney(1500)).toBe("$1,500");
  });
});
