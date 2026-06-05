# Fix Responsive Navigation Bar

## 任务

导航栏在 390px 宽度下产生横向溢出，用户需要水平滚动才能看到完整导航。请修复响应式布局。

你需要：
1. 查看 `src/Navbar.jsx` 和 `styles/nav.css`
2. 修复布局使导航栏在 390px 宽度下不溢出
3. 可以使用汉堡菜单或折叠式导航
4. 运行 `pytest tests/ -v` 确认测试通过
5. 在 `design_notes.md` 中说明修改

## 要求

- 390px viewport 下 `scrollWidth <= viewport width`
- 所有导航链接在某种方式下仍可访问
