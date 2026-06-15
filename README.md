# 🧩 8-Puzzle Solver & AI Search Algorithms Simulation

Đồ án/Bài tập môn **Trí tuệ Nhân tạo (Artificial Intelligence)**.
Chương trình mô phỏng trực quan toàn diện các thuật toán tìm kiếm cốt lõi trong Trí tuệ Nhân tạo, từ không gian trạng thái cơ bản đến các môi trường phức tạp và bài toán thỏa mãn ràng buộc. 

Đặc biệt, công cụ này được thiết kế như một phần mềm hỗ trợ học tập, có khả năng tự động sinh **Bảng vết (Trace Table)** với các bước xử lý (Node, Frontier, Reached) chuẩn xác tuyệt đối theo cách ghi chép trong giáo trình Đại học.

---

## 📌 Thông tin Sinh viên
* **Họ và tên:** Phạm Đăng Khoa
* **MSSV:** 24110256
* **Môn học:** Trí tuệ Nhân tạo (AI)

---

## ✨ Tính năng nổi bật

1. **Giao diện trực quan (GUI):** Xây dựng bằng thư viện `Tkinter`, dễ dàng nhập và quan sát tiến trình thay đổi của các trạng thái.
2. **Kiểm tra tính giải được (Solvability Check):** Tự động tính toán Inversions (số lượng nghịch thế). Hệ thống cảnh báo ngay lập tức nếu bài toán vô nghiệm để chặn đứng rủi ro tràn RAM.
3. **Sinh Bảng Vết (Trace Table) chuẩn giáo trình:**
   * Tự động gán nhãn đại diện A, B, C... cho các đỉnh.
   * Hiển thị rõ ràng 3 cột chuẩn: `NODE` | `FRONTIER` | `REACHED`.
   * Trình bày thông minh, tự động thay đổi cú pháp in chi phí tùy theo thuật toán (`depth`, `g`, `h`, hoặc `f(g+h)`). 
   * Xử lý hiển thị thông minh: Tự động ép phẳng ma trận (thành dạng mảng chuỗi) khi biểu diễn Tập niềm tin (Belief State) để chống vỡ bảng.
4. **Trình phát lại (Playback):** Hỗ trợ mô phỏng tự động chạy hoặc tiến/lùi từng bước để quan sát chi tiết ma trận di chuyển sau khi tìm ra đường đi tối ưu.
5. **Môi trường giả lập nâng cao:** Hỗ trợ mô phỏng đa dạng các bài toán thực tế: Môi trường khuyết thông tin (Sensorless, Multiple Goals), Môi trường không tất định (Nondeterministic) và Tô màu bản đồ (Map Coloring).

---

## 🧠 Các thuật toán được triển khai

Hệ thống bao phủ 5 nhóm thuật toán chính trong khoa học Trí tuệ Nhân tạo:

### 1. Tìm kiếm mù (Uninformed Search)
* **BFS (Breadth-First Search):** Có 2 phiên bản xử lý và đánh giá tập Reached/Frontier khác nhau.
* **DFS (Depth-First Search):** Có 2 phiên bản ưu tiên duyệt sâu.
* **IDS (Iterative Deepening Search):** Tìm kiếm sâu dần kết hợp giới hạn độ sâu linh hoạt.

### 2. Tìm kiếm có thông tin (Informed Search)
* **UCS (Uniform Cost Search):** Ưu tiên duyệt đỉnh có chi phí $g(n)$ nhỏ nhất (đếm số ô sai vị trí so với đích).
* **Greedy Search (Tìm kiếm Tham lam):** Ưu tiên duyệt đỉnh có chi phí Heuristic $h(n)$ nhỏ nhất (Sử dụng khoảng cách Manhattan).
* **A* (A-Star Search):** Tìm đường đi tối ưu thông qua hàm đánh giá $f(n) = g(n) + h(n)$.
* **IDA* (Iterative Deepening A*):** Thuật toán bộ nhớ hẹp, kết hợp DFS sâu dần với hàm đánh giá $f(n)$ của A*.

### 3. Tìm kiếm cục bộ (Local Search)
Mục tiêu là đưa hàm $h(n)$ (Khoảng cách Manhattan) về điểm cực tiểu cục bộ/toàn cục:
* **Simple Hill Climbing (Leo đồi đơn giản):** Khảo sát lần lượt từng lân cận, chuyển ngay lập tức nếu có 1 lân cận tốt hơn.
* **Steepest-Ascent Hill Climbing (Leo đồi dốc nhất):** Khảo sát TOÀN BỘ lân cận, tìm ra trạng thái có $h(n)$ thấp nhất rồi mới quyết định chuyển trạng thái.
* **Stochastic Hill Climbing (Leo đồi ngẫu nhiên):** Sinh toàn bộ lân cận để lọc ra tập các trạng thái tốt hơn (`Better_Neighbors`), sau đó lựa chọn ngẫu nhiên 1 trạng thái để đi tiếp.
* **Random-Restart Hill Climbing:** Thực hiện Stochastic Hill Climbing kết hợp cơ chế khởi động lại vòng lặp nếu rơi vào trạng thái bế tắc (Giới hạn `MAX_RESTART = 5`).
* **Local Beam Search (Tìm kiếm chùm cục bộ):** Khởi tạo từ $k=3$ trạng thái ngẫu nhiên. Sau mỗi vòng lặp, duyệt toàn bộ lân cận của chùm và chọn giữ lại đúng $k$ trạng thái ưu tú nhất.
* **Simulated Annealing (Tôi luyện mô phỏng):** Sử dụng phân bố xác suất $p = e^{-\Delta E / T}$ cho phép Agent thỉnh thoảng chấp nhận các trạng thái "tệ hơn" để lấy đà thoát khỏi cực tiểu cục bộ. Nhiệt độ $T$ được kiểm soát giảm dần.

### 4. Tìm kiếm trong môi trường phức tạp
Xử lý các vấn đề khuyết thông tin (Partial Observable) và không tất định (Nondeterministic):
* **Khuyết Start (Sensorless / Belief State):** Bắt đầu trạng thái mù bằng một *Tập niềm tin* chứa các trạng thái xuất phát khả dĩ. Agent sử dụng BFS để tìm chuỗi hành động ép buộc (Coercion Sequence) nhằm thu hẹp tập niềm tin cho đến khi 100% đạt đích.
* **Khuyết Goal (Đa đích / Multiple Goals):** Môi trường tồn tại một tập các đích khả dĩ. Agent tiến hành dò đường cho đến khi thỏa mãn bất kỳ đích nào trong tập.
* **Khuyết một phần (Auto-complete):** Môi trường bị che khuất dấu `*`. Hệ thống dùng Parity Check khôi phục lại cấu hình hợp lệ và tự do cho phép chọn chéo các thuật toán cơ sở (A*, BFS...) để giải.
* **Hành động không rõ ràng (AND-OR Graph Search):** Giả lập môi trường bị trơn trượt (Agent ra lệnh nhưng ô không di chuyển). Duyệt cây AND-OR để xuất ra một **Kế hoạch dự phòng (Contingency Plan)** chứa các biểu thức logic `If-Then`.

### 5. Thỏa mãn ràng buộc (Constraint Satisfaction Problem - CSP)
* **Bài toán Tô màu bản đồ (Map Coloring):** Giải quyết đồ thị tô màu các bang của Úc.
* **Thuật toán Backtracking (Quay lui):** * Áp dụng quy trình chuẩn: Lựa chọn biến chưa gán (Select-Unassigned-Variable), thử miền giá trị (Order-Domain-Values) và kiểm tra tính nhất quán với vùng kề (Consistent).
  * Ghi nhận log chi tiết từng bước thử và tự động quay lui khi phát hiện vi phạm ràng buộc.

---

## 🚀 Cài đặt & Sử dụng

### Yêu cầu hệ thống
* Môi trường: Python 3.x.
* Thư viện: `tkinter` (Thường được cài sẵn kèm bộ lõi Python).

### Cách khởi chạy
1. Clone repository về thiết bị cục bộ:
   ```bash
   git clone [https://github.com/phamdangkhoa3165-cmd/AI.git](https://github.com/phamdangkhoa3165-cmd/AI.git)
   
2. Khởi chạy bằng Jupyter Notebook hoặc chạy trực tiếp bằng Python:
   python UI_8_puzzle.py