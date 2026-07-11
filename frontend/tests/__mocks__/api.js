/**
 * Mock Axios API 模块
 * 各测试用例可通过 vi.mocked() 动态设置返回值
 */
import { vi } from "vitest";

const mockGet = vi.fn();

export const fetchMovies = vi.fn();
export const fetchMovieDetail = vi.fn();
export const fetchStats = vi.fn();
export const fetchGenres = vi.fn();
export const fetchYears = vi.fn();
export const fetchCountries = vi.fn();

export default { get: mockGet };
