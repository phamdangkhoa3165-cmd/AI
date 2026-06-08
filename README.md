# 🧩 8-Puzzle Solver & Trace Table Generator

Bài tập môn **Trí tuệ Nhân tạo (Artificial Intelligence)**.
Chương trình mô phỏng trực quan các thuật toán tìm kiếm trên không gian trạng thái để giải quyết bài toán 8-Puzzle. Đặc biệt, công cụ này tự động sinh ra **Bảng vết (Trace Table)** với các bước xử lý (Node, Frontier, Reached) chuẩn xác như cách ghi chép trong vở trên lớp học.

---

## 📌 Thông tin Sinh viên
* **Họ và tên:** Phạm Đăng Khoa
* **MSSV:** 24110256
* **Môn học:** Trí tuệ Nhân tạo (AI)

---

## ✨ Tính năng nổi bật

1. **Giao diện trực quan (GUI):** Xây dựng bằng `Tkinter`, dễ dàng nhập trạng thái Start và Goal.
2. **Kiểm tra tính giải được (Solvability Check):** Tự động tính toán Inversions (số cặp nghịch thế). Cảnh báo ngay nếu bài toán vô nghiệm để tránh tràn RAM.
3. **Sinh Bảng Vết (Trace Table) chuẩn giáo trình:**
   * Tự động gán nhãn A, B, C, D... cho các đỉnh.
   * Hiển thị rõ ràng 3 cột: `NODE` | `FRONTIER` | `REACHED`.
   * Trình bày thông minh, tự động thay đổi cú pháp hiển thị chi phí tùy theo thuật toán (`depth`, `g`, `h`, hoặc `f(g+h)`). Ép phẳng ma trận (Belief State) đối với môi trường phức tạp để chống vỡ bảng.
4. **Trình phát lại (Playback):** Chế độ tự động chạy hoặc tiến/lùi từng bước để xem cách ma trận di chuyển sau khi tìm thấy đường đi đích.
5. **Môi trường giả lập nâng cao:** Hỗ trợ mô phỏng môi trường khuyết thông tin (Sensorless, Multiple Goals) với menu thả xuống (Combobox) cho phép tự do chọn thuật toán giải quyết.

---

## 🧠 Các thuật toán được triển khai

### 1. Tìm kiếm mù (Uninformed Search)
* **BFS (Breadth-First Search):** Có 2 phiên bản xử lý tập Reached/Frontier khác nhau.
* **DFS (Depth-First Search):** Có 2 phiên bản ưu tiên độ sâu.
* **IDS (Iterative Deepening Search):** Tìm kiếm sâu dần có giới hạn độ sâu.

### 2. Tìm kiếm có thông tin (Informed Search)
* **UCS (Uniform Cost Search):** Ưu tiên duyệt đỉnh có chi phí $g(n)$ nhỏ nhất (đếm số ô sai vị trí).
* **Greedy Search (Tìm kiếm Tham lam):** Ưu tiên duyệt đỉnh có $h(n)$ nhỏ nhất (khoảng cách Manhattan).
* **A* (A-Star Search):** Hàm đánh giá $f(n) = g(n) + h(n)$.
* **IDA* (Iterative Deepening A*):** Kết hợp DFS sâu dần với hàm đánh giá $f(n)$ của A*.

### 3. Tìm kiếm cục bộ (Local Search)
Mục tiêu là đưa hàm $h(n)$ (Khoảng cách Manhattan) về cực tiểu.
* **Simple Hill Climbing (Leo đồi đơn giản):** Khảo sát từng lân cận, nếu có 1 lân cận tốt hơn sẽ chuyển ngay lập tức.
* **Steepest-Ascent Hill Climbing (Leo đồi dốc nhất):** Sinh TOÀN BỘ lân cận, tìm ra lân cận có $h(n)$ thấp nhất rồi mới quyết định chuyển trạng thái.
* **Stochastic Hill Climbing (Leo đồi ngẫu nhiên):** Sinh toàn bộ lân cận để lọc ra tập trạng thái tốt hơn (`Better_Neighbors`), sau đó lựa chọn ngẫu nhiên 1 trạng thái trong tập này.
* **Random-Restart Hill Climbing:** Thực hiện Stochastic Hill Climbing. Nếu rơi vào cực tiểu cục bộ (bế tắc), thuật toán sẽ khởi động lại vòng lặp (Giới hạn `MAX_RESTART = 5`).
* **Local Beam Search (Tìm kiếm chùm cục bộ):** Khởi tạo bằng $k=3$ trạng thái ngẫu nhiên. Mỗi bước sinh toàn bộ lân cận của chùm và chỉ giữ lại đúng $k$ trạng thái tốt nhất.
* **Simulated Annealing (Luyện kim sa / Tôi luyện mô phỏng):** Sử dụng hàm phân bố xác suất $p = e^{-\Delta E / T}$ để cho phép Agent đôi khi chấp nhận các trạng thái "tệ hơn" nhằm thoát khỏi cực tiểu cục bộ. Nhiệt độ $T$ giảm dần theo thời gian.

### 4. Tìm kiếm trong môi trường phức tạp (Khuyết thông tin)
* **Khuyết Start (Sensorless / Belief State):** Bắt đầu mù bằng một *Tập niềm tin* chứa các trạng thái xuất phát khả dĩ. Agent thực hiện chuỗi hành động ép buộc (Coercion) để thu hẹp tập niềm tin cho đến khi chắc chắn 100% đạt đích.
* **Khuyết Goal (Đa đích / Multiple Goals):** Môi trường tồn tại một tập hợp các đích khả dĩ. Agent tiến hành tìm đường cho đến khi chạm vào bất kỳ đích nào trong tập.
* **Khuyết một phần (Auto-complete):** Môi trường bị che khuất một vài ô `*`. Thuật toán sẽ dùng chẵn lẻ Parity Check để khôi phục lại cấu hình hợp lệ chắc chắn giải được.
> 💡 *Đặc biệt:* Module này được tích hợp Combobox cho phép người dùng tự do áp dụng chéo các thuật toán cơ sở (BFS, DFS, UCS, Greedy, A*) vào việc thu hẹp Belief State hoặc dò tìm Multi-goal.

---

## 🚀 Cài đặt & Sử dụng

### Yêu cầu hệ thống
* Python 3.x.
* Thư viện `tkinter` (Thường được cài sẵn kèm theo Python).

### Cách chạy chương trình
1. Clone repository về máy:
   https://github.com/phamdangkhoa3165-cmd/AI
   
2. Mở file `UI_8_puzzle.ipynb` hoặc `UI_8_puzzle.py` bằng IDE (VS Code, Jupyter...) và tiến hành chạy mã nguồn.