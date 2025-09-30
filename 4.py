import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import math

class LensRasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №4 (Вариант 17): Линза")
        self.image = None
        self.canvas_size = 600

        # --- Интерфейс ---
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_label = tk.Label(root, bg="white")
        self.canvas_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Ввод параметров
        tk.Label(control_frame, text="Параметры линзы", font=("Arial", 10, "bold")).pack(pady=5, anchor='w')
        param_frame = tk.Frame(control_frame)
        param_frame.pack(anchor='w', padx=5)
        
        tk.Label(param_frame, text="Радиус R1:").grid(row=0, column=0, sticky='w')
        self.r1_entry = tk.Entry(param_frame, width=5)
        self.r1_entry.grid(row=0, column=1, padx=5)
        self.r1_entry.insert(0, "200")

        tk.Label(param_frame, text="Радиус R2:").grid(row=1, column=0, sticky='w')
        self.r2_entry = tk.Entry(param_frame, width=5)
        self.r2_entry.grid(row=1, column=1, padx=5)
        self.r2_entry.insert(0, "200")

        tk.Label(param_frame, text="Толщина t:").grid(row=2, column=0, sticky='w')
        self.t_entry = tk.Entry(param_frame, width=5)
        self.t_entry.grid(row=2, column=1, padx=5)
        self.t_entry.insert(0, "50")
        
        tk.Button(control_frame, text="Создать/Очистить холст", command=self.create_canvas).pack(pady=10, fill=tk.X)

        # Кнопки для алгоритмов
        tk.Label(control_frame, text="Алгоритмы", font=("Arial", 10, "bold")).pack(pady=5, anchor='w')
        tk.Button(control_frame, text="1. Уравнение окружности", command=lambda: self.draw_lens('equation')).pack(pady=2, fill=tk.X)
        tk.Button(control_frame, text="2. Параметрическое ур-ние", command=lambda: self.draw_lens('parametric')).pack(pady=2, fill=tk.X)
        tk.Button(control_frame, text="3. Алгоритм Брезенхема", command=lambda: self.draw_lens('bresenham')).pack(pady=2, fill=tk.X)
        tk.Button(control_frame, text="4. Встроенный метод", command=lambda: self.draw_lens('builtin')).pack(pady=2, fill=tk.X)

        # Сохранение
        tk.Label(control_frame, text="Сохранение", font=("Arial", 10, "bold")).pack(pady=10, anchor='w')
        tk.Button(control_frame, text="Сохранить как (PNG, JPG...)", command=self.save_image).pack(pady=2, fill=tk.X)
        tk.Button(control_frame, text="Сохранить в PBM (ч/б текст)", command=self.save_as_pbm).pack(pady=2, fill=tk.X)
        # --- НОВАЯ КНОПКА ---
        tk.Button(control_frame, text="Сохранить в PPM P3 (цветной текст)", command=self.save_as_ppm).pack(pady=2, fill=tk.X)
        
        self.create_canvas()

    def create_canvas(self):
        self.image = Image.new('RGB', (self.canvas_size, self.canvas_size), 'white')
        self._update_display()
        print(f"Холст {self.canvas_size}x{self.canvas_size} создан.")

    def _update_display(self):
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas_label.config(image=self.photo_image)
    
    def _plot_pixel(self, x, y, color):
        if 0 <= x < self.image.width and 0 <= y < self.image.height:
            self.image.putpixel((int(x), int(y)), color)

    def draw_lens(self, method):
        try:
            r1, r2, t = int(self.r1_entry.get()), int(self.r2_entry.get()), int(self.t_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры должны быть целыми числами.")
            return

        canvas_center = self.canvas_size / 2
        dist_centers = r1 + r2 - t
        if dist_centers <= 0 or r1 <= t/2 or r2 <= t/2 or abs(r1-r2) > dist_centers:
            messagebox.showwarning("Ошибка геометрии", "Невозможно построить линзу с такими параметрами.")
            return

        c1x, c2x = canvas_center - r1 + t/2, canvas_center + r2 - t/2
        x_tip = (dist_centers**2 - r2**2 + r1**2) / (2 * dist_centers)
        x_tip_abs = c1x + x_tip
        
        if r1**2 - x_tip**2 < 0:
            messagebox.showwarning("Ошибка геометрии", "Окружности не пересекаются.")
            return
            
        y_tip = math.sqrt(r1**2 - x_tip**2)

        color_map = {'equation': (255,0,0), 'parametric': (0,128,0), 'bresenham': (0,0,255), 'builtin': (0,0,0)}
        color = color_map[method]
        
        if method == 'builtin':
            self.draw_arc_builtin(c1x, canvas_center, r1, -y_tip, y_tip, color)
            self.draw_arc_builtin(c2x, canvas_center, r2, -y_tip, y_tip, color)
        else:
            self.draw_arc_generic(method, c1x, canvas_center, r1, x_tip_abs, "left", color)
            self.draw_arc_generic(method, c2x, canvas_center, r2, x_tip_abs, "right", color)

        self._update_display()

    def draw_arc_generic(self, method, xc, yc, r, x_boundary, arc_side, color):
        if method == 'bresenham':
            x, y = 0, r
            delta = 2 - 2 * r
            while y >= x:
                if arc_side == "left":
                    if xc + x >= x_boundary: self._plot_pixel(xc + x, yc + y, color); self._plot_pixel(xc + x, yc - y, color)
                    if xc + y >= x_boundary: self._plot_pixel(xc + y, yc + x, color); self._plot_pixel(xc + y, yc - x, color)
                elif arc_side == "right":
                    if xc - x <= x_boundary: self._plot_pixel(xc - x, yc + y, color); self._plot_pixel(xc - x, yc - y, color)
                    if xc - y <= x_boundary: self._plot_pixel(xc - y, yc + x, color); self._plot_pixel(xc - y, yc - x, color)
                d1, d2 = 2 * (delta + y) - 1, 2 * (delta - x) - 1
                if delta < 0 and d1 <= 0: delta += 2 * (x := x + 1) + 1
                elif delta > 0 and d2 > 0: delta -= 2 * (y := y - 1) + 1
                else: delta += 2 * ((x := x + 1) - (y := y - 1)) + 2
        
        if method == 'equation':
            for x_offset in range(int(r / math.sqrt(2)) + 1):
                y_offset = round(math.sqrt(max(0, r**2 - x_offset**2)))
                if arc_side == "left":
                    if xc + x_offset >= x_boundary: self._plot_pixel(xc + x_offset, yc + y_offset, color); self._plot_pixel(xc + x_offset, yc - y_offset, color)
                    if xc + y_offset >= x_boundary: self._plot_pixel(xc + y_offset, yc + x_offset, color); self._plot_pixel(xc + y_offset, yc - x_offset, color)
                elif arc_side == "right":
                    if xc - x_offset <= x_boundary: self._plot_pixel(xc - x_offset, yc + y_offset, color); self._plot_pixel(xc - x_offset, yc - y_offset, color)
                    if xc - y_offset <= x_boundary: self._plot_pixel(xc - y_offset, yc + x_offset, color); self._plot_pixel(xc - y_offset, yc - x_offset, color)
       
        if method == 'parametric':
            step, t = 1 / r, 0
            while t <= 2 * math.pi:
                x, y = r * math.cos(t), r * math.sin(t)
                if (arc_side == "left" and xc + x >= x_boundary) or \
                   (arc_side == "right" and xc + x <= x_boundary):
                    self._plot_pixel(xc + x, yc + y, color)
                t += step

    def draw_arc_builtin(self, xc, yc, r, y_start, y_end, color):
        draw = ImageDraw.Draw(self.image)
        bounding_box = [xc - r, yc - r, xc + r, yc + r]
        try:
            x_for_y_start = math.sqrt(r**2 - y_start**2)
        except ValueError: return
        angle_bottom = math.degrees(math.atan2(y_start, x_for_y_start))
        angle_top = math.degrees(math.atan2(y_end, x_for_y_start))
        if xc < self.canvas_size / 2: start_angle, end_angle = angle_bottom, angle_top
        else: start_angle, end_angle = 180 - angle_top, 180 - angle_bottom
        if start_angle > end_angle: start_angle, end_angle = end_angle, start_angle
        draw.arc(bounding_box, start=start_angle, end=end_angle, fill=color, width=1)

    def save_image(self):
        if not self.image:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("Успех", f"Изображение сохранено в {file_path}")

    def save_as_pbm(self):
        if not self.image:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pbm",
            filetypes=[("PBM file", "*.pbm"), ("All files", "*.*")]
        )
        if not file_path: return

        width, height = self.image.size
        try:
            with open(file_path, 'w') as f:
                f.write("P1\n")
                f.write(f"# Lens R1={self.r1_entry.get()}, R2={self.r2_entry.get()}, t={self.t_entry.get()}\n")
                f.write(f"{width} {height}\n")
                
                for y in range(height):
                    row_data = []
                    for x in range(width):
                        r, g, b = self.image.getpixel((x, y))
                        brightness = (r + g + b) / 3
                        row_data.append("1" if brightness < 128 else "0")
                    f.write(" ".join(row_data) + "\n")
            
            messagebox.showinfo("Успех", f"Изображение успешно сохранено в PBM формате:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

  
    def save_as_ppm(self):
        """Конвертирует изображение в текстовый цветной формат PPM P3."""
        if not self.image:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            filetypes=[("PPM file", "*.ppm"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return

        width, height = self.image.size
        
        try:
            with open(file_path, 'w') as f:
                # 1. Заголовок PPM P3
                f.write("P3\n")
                f.write(f"# Lens R1={self.r1_entry.get()}, R2={self.r2_entry.get()}, t={self.t_entry.get()}\n")
                f.write(f"{width} {height}\n")
                f.write("255\n") # Максимальное значение цвета
                
                # 2. Данные пикселей (R G B)
                for y in range(height):
                    row_data = []
                    for x in range(width):
                        r, g, b = self.image.getpixel((x, y))
                        row_data.append(str(r))
                        row_data.append(str(g))
                        row_data.append(str(b))
                    # Записываем строку пикселей (R G B R G B ...) в файл
                    f.write(" ".join(row_data) + "\n")
            
            messagebox.showinfo("Успех", f"Изображение успешно сохранено в PPM P3 формате:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LensRasterizationApp(root)
    root.mainloop()