# Chạy AI-SIEM-SOAR trên máy local

## Windows PowerShell

```powershell
cd <thu-muc-clone-repo>
.\scripts\setup_windows.ps1
.\.venv\Scripts\python.exe -m orchestrator.main check
.\.venv\Scripts\python.exe -m orchestrator.main demo
```

Nếu PowerShell chặn script, dùng:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

## Ubuntu/Linux

```bash
cd <thu-muc-clone-repo>
chmod +x scripts/setup_linux.sh scripts/run_linux.sh
./scripts/setup_linux.sh
./scripts/run_linux.sh check
./scripts/run_linux.sh demo
```

## Ollama

Ollama là tùy chọn ở giai đoạn framework. Nếu Ollama đang chạy ở host với API mặc định:

```powershell
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
.\.venv\Scripts\python.exe -m orchestrator.main ollama
```

Nếu chạy được, lệnh sẽ liệt kê các model hiện có. Repository không khóa model cụ thể; model sẽ được cấu hình sau.

## Kết quả mong đợi

- `check`: đọc workflow state, phát hiện 4 agent, kiểm tra Tool Registry và Ollama executable.
- `demo`: chạy toàn bộ pytest thông qua Tool Gateway và trả về exit code.
- Audit events được ghi vào `.ai/audit/`.

## Nguyên tắc an toàn

- Không có arbitrary shell cho agent.
- Test command dùng argv list thay vì chuỗi shell.
- Không chạy kiểm thử tấn công vào hệ thống bên ngoài.
- SOAR action thật sẽ chỉ được mở sau khi policy, permission và human gate được hoàn thiện.
