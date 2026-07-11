/**
 * localStorage 收藏工具
 *
 * 存储格式：JSON 数组，存放已收藏的电影 id
 * 例：[1, 5, 23, 100]
 */

const STORAGE_KEY = "metamovie_favorites";

// ---------------------------------------------------------------------------
// 内部：读取原始数组
// ---------------------------------------------------------------------------
function _read() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// 内部：写入原始数组
// ---------------------------------------------------------------------------
function _write(ids) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
  } catch {
    // localStorage 满了或隐私模式被禁 — 静默失败
  }
}

// ---------------------------------------------------------------------------
// 公开 API
// ---------------------------------------------------------------------------

/** 返回收藏的电影 id 列表（新数组，外部修改安全） */
export function getFavorites() {
  return [..._read()];
}

/** 切换收藏状态，返回切换后的状态（true=已收藏, false=已取消） */
export function toggleFavorite(id) {
  const ids = _read();
  const idx = ids.indexOf(id);
  if (idx === -1) {
    ids.push(id);
    _write(ids);
    return true;
  } else {
    ids.splice(idx, 1);
    _write(ids);
    return false;
  }
}

/** 判断是否已收藏 */
export function isFavorite(id) {
  return _read().includes(id);
}

/** 获取收藏数量 */
export function getFavoriteCount() {
  return _read().length;
}
