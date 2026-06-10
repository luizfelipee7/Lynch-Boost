import platform
import os
import subprocess
import json

# Tenta importar psutil para os fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Tenta importar win32com.client para os fallbacks WMI
try:
    import win32com.client
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

def formatar_cache(kb):
    if not kb:
        return "N/A"
    mb = kb / 1000
    if mb >= 10:
        return f"{mb:.1f} MB"
    else:
        return f"{mb:.2f} MB"

def obter_dados_hardware():
    dados = {
        "cpu": [],
        "ram_slots": [],
        "ram_uso": {},
        "gpu": [],
        "disks": [],
        "motherboard": {
            "fabricante": "Desconhecido", "product": "Desconhecido", "version": "",
            "system": "", "chipset": "", "model": "", "revision": "",
            "bios_manufacturer": "", "bios_name": "", "bios_version": "", "bios_build": ""
        },
        "os": {
            "nome": "Desconhecido", 
            "arquitetura": "Desconhecido", 
            "build": "Desconhecido",
            "uptime": "N/A",
            "install_date": "N/A",
            "secure_boot": "N/A",
            "directx": "N/A",
            "csm": "N/A",
            "fast_startup": "N/A"
        }
    }

    # 1. QUERY POWERSHELL (Garante 100% dos dados reais sem precisar de dependências)
    ps_script = """
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version, TotalVisibleMemorySize, FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory, DataExecutionPrevention_Available, LastBootUpTime, InstallDate
    $board = Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version
    $system = Get-CimInstance Win32_ComputerSystem | Select-Object Model
    $chipset = Get-CimInstance Win32_IDEController | Select-Object Name
    $bios = Get-CimInstance Win32_BIOS | Select-Object Manufacturer, Name, Version, BuildNumber
    $cpu = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, L2CacheSize, L3CacheSize, VirtualizationFirmwareEnabled, LoadPercentage, Stepping, Revision
    
    # GPU WMI Info
    $gpu = Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM, VideoMemoryType, AdapterDACType, CurrentHorizontalResolution, CurrentVerticalResolution, CurrentRefreshRate
    $3dEngines = Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | Where-Object { $_.Name -like "*engtype_3D" }
    $gpuUsage = ($3dEngines | Measure-Object -Property UtilizationPercentage -Sum).Sum
    if ($gpuUsage -gt 100) { $gpuUsage = 100 }
    
    $ram = Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Manufacturer, Capacity, Speed, FormFactor
    $disks = Get-CimInstance Win32_DiskDrive | ForEach-Object {
        $dd = $_
        $pd = Get-PhysicalDisk -ErrorAction SilentlyContinue | Where-Object { [string]$_.DeviceId -eq [string]$dd.Index }
        $diskType = "SSD/HDD"
        if ($pd) {
            $diskType = $pd.MediaType.ToString()
        }
        [PSCustomObject]@{
            Model = $dd.Model
            Size = $dd.Size
            FirmwareRevision = $dd.FirmwareRevision
            MediaType = $dd.MediaType
            BytesPerSector = $dd.BytesPerSector
            DiskType = $diskType
        }
    }

    # Calcular Uptime do Sistema
    $uptime = (Get-Date) - $os.LastBootUpTime
    $uptimeStr = "{0}d {1}h {2}m" -f $uptime.Days, $uptime.Hours, $uptime.Minutes

    # Formatar Data de Instalacao
    $installDateStr = $os.InstallDate.ToString("dd/MM/yyyy HH:mm")

    # Secure Boot
    $secureBoot = if ((Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\SecureBoot\\State" -ErrorAction SilentlyContinue).UEFISecureBootEnabled -eq 1) { "Ativado" } else { "Desativado" }

    # DirectX Version
    $dx = "DirectX 11"
    if ([System.Environment]::OSVersion.Version.Major -ge 10) { $dx = "DirectX 12" }

    # CSM Status (Firmware Boot Type)
    $firmwareType = (Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control" -ErrorAction SilentlyContinue).PEFirmwareType
    $csm = if ($firmwareType -eq 1) { "Ativado (Legacy)" } else { "Desativado (UEFI)" }

    # Fast Startup
    $fastStartup = if ((Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" -ErrorAction SilentlyContinue).HiberbootEnabled -eq 1) { "Ativado" } else { "Desativado" }

    [PSCustomObject]@{
        OS = $os
        Board = $board
        System = $system
        Chipset = $chipset
        Bios = $bios
        CPU = $cpu
        GPU = $gpu
        RAM = $ram
        Disks = $disks
        GPUUsage = $gpuUsage
        Uptime = $uptimeStr
        InstallDate = $installDateStr
        SecureBoot = $secureBoot
        DirectX = $dx
        CSM = $csm
        FastStartup = $fastStartup
    } | ConvertTo-Json -Depth 5
    """

    sucesso_ps = False
    try:
        process = subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0x08000000 # CREATE_NO_WINDOW
        )
        stdout_bytes, stderr_bytes = process.communicate(input=ps_script.encode('utf-8'), timeout=10)
        
        stdout = ""
        if stdout_bytes:
            for enc in ['utf-8', 'cp1252', 'latin-1', 'cp850']:
                try:
                    stdout = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if not stdout:
                stdout = stdout_bytes.decode('utf-8', errors='replace')
        
        if process.returncode == 0 and stdout.strip():
            raw_data = json.loads(stdout)
            sucesso_ps = True

            # PARSE OS
            os_info = raw_data.get("OS")
            if os_info:
                dados["os"] = {
                    "nome": os_info.get("Caption", "Windows").strip(),
                    "arquitetura": os_info.get("OSArchitecture", "64-bit").strip(),
                    "build": os_info.get("Version", "N/A").strip(),
                    "uptime": raw_data.get("Uptime", "N/A"),
                    "install_date": raw_data.get("InstallDate", "N/A"),
                    "secure_boot": raw_data.get("SecureBoot", "N/A"),
                    "directx": raw_data.get("DirectX", "N/A"),
                    "csm": raw_data.get("CSM", "N/A"),
                    "fast_startup": raw_data.get("FastStartup", "N/A")
                }

                # PARSE RAM USO
                tot_ram_kb = os_info.get("TotalVisibleMemorySize")
                free_ram_kb = os_info.get("FreePhysicalMemory")
                tot_virt_kb = os_info.get("TotalVirtualMemorySize")
                free_virt_kb = os_info.get("FreeVirtualMemory")

                if tot_ram_kb and free_ram_kb:
                    tot_ram_gb = tot_ram_kb / (1024 * 1024)
                    free_ram_gb = free_ram_kb / (1024 * 1024)
                    used_ram_gb = tot_ram_gb - free_ram_gb
                    pct_ram = int((used_ram_gb / tot_ram_gb) * 100) if tot_ram_gb else 0

                    tot_virt_gb = tot_virt_kb / (1024 * 1024) if tot_virt_kb else tot_ram_gb
                    free_virt_gb = free_virt_kb / (1024 * 1024) if free_virt_kb else free_ram_gb
                    used_virt_gb = tot_virt_gb - free_virt_gb
                    pct_virt = int((used_virt_gb / tot_virt_gb) * 100) if tot_virt_gb else 0

                    dados["ram_uso"] = {
                        "total_fisica": f"{tot_ram_gb:.2f} GiB",
                        "usado_fisica": f"{used_ram_gb:.2f} GiB",
                        "percentual_fisica": pct_ram,
                        "total_virtual": f"{tot_virt_gb:.2f} GiB",
                        "disponivel_virtual": f"{free_virt_gb:.2f} GiB",
                        "usada_virtual": f"{used_virt_gb:.2f} GiB",
                        "percentual_virtual": pct_virt
                    }

            # PARSE BOARD & BIOS
            board_info = raw_data.get("Board")
            sys_info = raw_data.get("System")
            chip_info = raw_data.get("Chipset")
            bios_info = raw_data.get("Bios")
            
            chip_name = ""
            if chip_info:
                chips_list = chip_info if isinstance(chip_info, list) else [chip_info]
                if chips_list:
                    chip_name = chips_list[0].get("Name", "")
                    
            dados["motherboard"] = {
                "fabricante": board_info.get("Manufacturer", "Desconhecido").strip() if board_info else "Desconhecido",
                "product": board_info.get("Product", "Desconhecido").strip() if board_info else "Desconhecido",
                "version": board_info.get("Version", "").strip() if board_info else "",
                "system": sys_info.get("Model", "").strip() if sys_info else "",
                "chipset": chip_name.strip(),
                "model": "", # Conforme imagem (vazio)
                "revision": "", # Conforme imagem (vazio)
                
                # BIOS
                "bios_manufacturer": bios_info.get("Manufacturer", "").strip() if bios_info else "",
                "bios_name": bios_info.get("Name", "").strip() if bios_info else "",
                "bios_version": bios_info.get("Version", "").strip() if bios_info else "",
                "bios_build": str(bios_info.get("BuildNumber", "")) if bios_info and bios_info.get("BuildNumber") is not None else ""
            }

            # PARSE CPU
            cpu_raw = raw_data.get("CPU")
            if cpu_raw:
                cpus_list = cpu_raw if isinstance(cpu_raw, list) else [cpu_raw]
                
                # Monta a string stepping do registro/sistema operacional
                stepping_str = os.environ.get("PROCESSOR_IDENTIFIER", platform.processor() or "")
                for sub in [", AuthenticAMD", ", GenuineIntel"]:
                    if sub in stepping_str:
                        stepping_str = stepping_str.replace(sub, "")
                stepping_str = stepping_str.strip()

                for cpu in cpus_list:
                    l2_kb = cpu.get("L2CacheSize", 0)
                    l3_kb = cpu.get("L3CacheSize", 0)

                    # Virtualização e DEP
                    virt_val = cpu.get("VirtualizationFirmwareEnabled")
                    virt_str = "Sim" if virt_val is True else "Não" if virt_val is False else "N/A"
                    
                    dep_val = os_info.get("DataExecutionPrevention_Available") if os_info else None
                    dep_str = "Sim" if dep_val is True else "Não" if dep_val is False else "N/A"

                    # Nome limpo
                    cpu_nome = cpu.get("Name", "CPU Desconhecida").strip()
                    cpu_nome = " ".join(cpu_nome.split())

                    # Revisão
                    rev_val = cpu.get("Revision")
                    revision_str = str(rev_val) if rev_val is not None else "N/A"

                    dados["cpu"].append({
                        "nome": cpu_nome,
                        "cores_fisicos": cpu.get("NumberOfCores", 0),
                        "threads": cpu.get("NumberOfLogicalProcessors", 0),
                        "cache_l2": formatar_cache(l2_kb),
                        "cache_l3": formatar_cache(l3_kb),
                        "virtualizacao": virt_str,
                        "dep": dep_str,
                        "stepping": stepping_str,
                        "revision": revision_str,
                        "uso": float(cpu.get("LoadPercentage", 0.0))
                    })

            # PARSE GPU
            gpu_raw = raw_data.get("GPU")
            
            # Pega o uso de GPU em tempo real prioritariamente via nvidia-smi
            gpu_usage_total = 0.0
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=1, creationflags=0x08000000
                )
                if res.returncode == 0 and res.stdout.strip():
                    gpu_usage_total = float(res.stdout.strip())
            except Exception:
                gpu_usage_total = float(raw_data.get("GPUUsage", 0.0))

            if gpu_raw:
                gpus_list = gpu_raw if isinstance(gpu_raw, list) else [gpu_raw]
                for gpu in gpus_list:
                    mem_bytes = gpu.get("AdapterRAM", 0)
                    if mem_bytes and mem_bytes > 0:
                        vram_val = round(mem_bytes / (1024 ** 3))
                        vram_str = f"{vram_val} GiB"
                    else:
                        vram_str = "N/A"
                    
                    # Memory Type Mapping
                    mem_type_map = {
                        1: "Outro", 2: "Unknown", 3: "VRAM", 4: "DRAM", 5: "SRAM", 
                        6: "WRAM", 7: "EDO RAM", 8: "Signature Auxillary RAM", 
                        9: "SDRAM", 10: "SGRAM"
                    }
                    mtype_val = gpu.get("VideoMemoryType", 2)
                    mtype_str = mem_type_map.get(mtype_val, "Unknown")
                    
                    # Resolution and Refresh Rate
                    horiz = gpu.get("CurrentHorizontalResolution")
                    vert = gpu.get("CurrentVerticalResolution")
                    res_str = f"{horiz} x {vert}" if horiz and vert else "N/A"
                    
                    ref_rate = gpu.get("CurrentRefreshRate")
                    ref_str = f"{ref_rate} Hz" if ref_rate else "N/A"

                    dados["gpu"].append({
                        "nome": gpu.get("Name", "Placa de Vídeo").strip(),
                        "driver_versao": gpu.get("DriverVersion", "Desconhecido").strip(),
                        "vram": vram_str,
                        "vram_type": mtype_str,
                        "dac_type": gpu.get("AdapterDACType", "Desconhecido").strip(),
                        "resolucao": res_str,
                        "taxa_atualizacao": ref_str,
                        "uso": gpu_usage_total
                    })

            # PARSE RAM CANAIS
            ram_raw = raw_data.get("RAM")
            if ram_raw:
                rams_list = ram_raw if isinstance(ram_raw, list) else [ram_raw]
                for ram in rams_list:
                    cap_bytes = ram.get("Capacity", 0)
                    cap_gb = cap_bytes / (1024 ** 3) if cap_bytes else 0
                    ff_val = ram.get("FormFactor", 0)
                    form_factor = "DIMM" if ff_val == 8 else "SODIMM" if ff_val == 12 else "Outro"
                    
                    dados["ram_slots"].append({
                        "canal": ram.get("DeviceLocator", "Slot").strip(),
                        "fabricante": ram.get("Manufacturer", "Desconhecido").strip(),
                        "tamanho": f"{cap_gb:.0f} GiB" if cap_gb else "N/A",
                        "velocidade": f"{ram.get('Speed', 0)} MHz" if ram.get('Speed') else "N/A",
                        "form_factor": form_factor
                    })

            # PARSE DISKS
            disks_raw = raw_data.get("Disks")
            if disks_raw:
                disks_list = disks_raw if isinstance(disks_raw, list) else [disks_raw]
                for disk in disks_list:
                    size_bytes = disk.get("Size")
                    size_str = "N/A"
                    if size_bytes:
                        size_gb = size_bytes / 1e9
                        if size_gb >= 1000:
                            size_str = f"{size_gb / 1000:.2f} TB"
                        else:
                            size_str = f"{size_gb:.2f} GB"
                    
                    disk_type = disk.get("DiskType", "SSD/HDD").strip()
                    if disk_type == "Unspecified" or disk_type == "SSD/HDD":
                        # Tenta deduzir pelo modelo
                        model_upper = disk.get("Model", "").upper()
                        if "SSD" in model_upper or "NVME" in model_upper or "SA400" in model_upper or "SNV2S" in model_upper:
                            disk_type = "SSD"
                        elif "HDD" in model_upper or "WDC" in model_upper or "SEAGATE" in model_upper:
                            disk_type = "HD"
                        else:
                            disk_type = "SSD/HDD"
                    elif disk_type == "HDD":
                        disk_type = "HD"

                    dados["disks"].append({
                        "model": disk.get("Model", "Desconhecido").strip(),
                        "size": size_str,
                        "firmware": disk.get("FirmwareRevision", "N/A").strip(),
                        "media_type": disk.get("MediaType", "Desconhecido").strip(),
                        "bytes_sector": str(disk.get("BytesPerSector", "N/A")),
                        "disk_type": disk_type
                    })

    except Exception as e:
        print(f"Erro ao obter dados via PowerShell: {e}")
        sucesso_ps = False

    # 2. SE O POWERSHELL FALHAR (Raríssimo): FALLBACK VIA WMI/PSUTIL/PLATFORM
    if not sucesso_ps:
        # Consulta de fallback original
        wmi = None
        if HAS_WMI:
            try:
                import pythoncom
                pythoncom.CoInitialize()
                wmi = win32com.client.GetObject("winmgmts:")
            except Exception:
                wmi = None

        # Fallback OS
        dados["os"] = {
            "nome": platform.system() + " " + platform.release(),
            "arquitetura": platform.machine(),
            "build": platform.version(),
            "uptime": "N/A",
            "install_date": "N/A",
            "secure_boot": "N/A",
            "directx": "DirectX 12" if platform.release() in ["10", "11"] else "DirectX 11",
            "csm": "Desativado (UEFI)" if platform.release() == "11" else "N/A",
            "fast_startup": "N/A"
        }

        # Fallback CPU
        cpu_usage = 0.0
        try:
            if HAS_PSUTIL:
                cpu_usage = psutil.cpu_percent(interval=0.1)
        except Exception:
            pass

        if wmi:
            try:
                for cpu in wmi.InstancesOf("Win32_Processor"):
                    l2_size = getattr(cpu, 'L2CacheSize', 0)
                    l3_size = getattr(cpu, 'L3CacheSize', 0)
                    dados["cpu"].append({
                        "nome": cpu.Name.strip(),
                        "cores_fisicos": cpu.NumberOfCores,
                        "threads": cpu.NumberOfLogicalProcessors,
                        "cache_l2": formatar_cache(l2_size),
                        "cache_l3": formatar_cache(l3_size),
                        "virtualizacao": "Sim" if getattr(cpu, 'VirtualizationFirmwareEnabled', False) else "Não",
                        "dep": "N/A",
                        "stepping": platform.processor(),
                        "revision": getattr(cpu, 'Revision', 'N/A'),
                        "uso": cpu_usage
                    })
            except Exception:
                pass

        if not dados["cpu"]:
            cores_fis = psutil.cpu_count(logical=False) if HAS_PSUTIL else 2
            threads_log = psutil.cpu_count(logical=True) if HAS_PSUTIL else 4
            dados["cpu"].append({
                "nome": platform.processor() or "Processador Desconhecido",
                "cores_fisicos": cores_fis,
                "threads": threads_log,
                "cache_l2": "N/A",
                "cache_l3": "N/A",
                "virtualizacao": "N/A",
                "dep": "N/A",
                "stepping": platform.processor(),
                "revision": "N/A",
                "uso": cpu_usage
            })

        # Fallback Motherboard
        if wmi:
            try:
                for board in wmi.InstancesOf("Win32_BaseBoard"):
                    dados["motherboard"] = {
                        "fabricante": getattr(board, 'Manufacturer', 'Desconhecido').strip(),
                        "product": getattr(board, 'Product', 'Desconhecido').strip(),
                        "version": getattr(board, 'Version', '').strip(),
                        "system": "", "chipset": "", "model": "", "revision": "",
                        "bios_manufacturer": "", "bios_name": "", "bios_version": "", "bios_build": ""
                    }
                    break
            except Exception:
                pass

        # Fallback GPU
        if wmi:
            try:
                for gpu in wmi.InstancesOf("Win32_VideoController"):
                    mem_bytes = getattr(gpu, 'AdapterRAM', 0)
                    vram_gb = f"{mem_bytes / (1024 ** 3):.1f} GB" if mem_bytes else "N/A"
                    dados["gpu"].append({
                        "nome": gpu.Name.strip(),
                        "driver_versao": getattr(gpu, 'DriverVersion', 'Desconhecido'),
                        "vram": vram_gb,
                        "vram_type": "Unknown",
                        "dac_type": getattr(gpu, 'AdapterDACType', 'Desconhecido'),
                        "resolucao": "N/A",
                        "taxa_atualizacao": "N/A",
                        "uso": 0.0
                    })
            except Exception:
                pass

        # Fallback RAM uso
        try:
            if HAS_PSUTIL:
                mem_virtual = psutil.virtual_memory()
                swap = psutil.swap_memory()
                total_sistema = (mem_virtual.total + swap.total) / (1024 ** 3)
                disponivel = (mem_virtual.available + swap.free) / (1024 ** 3)
                usado = total_sistema - disponivel
                
                dados["ram_uso"] = {
                    "total_fisica": f"{mem_virtual.total / (1024 ** 3):.2f} GiB",
                    "usado_fisica": f"{mem_virtual.used / (1024 ** 3):.2f} GiB",
                    "percentual_fisica": mem_virtual.percent,
                    "total_virtual": f"{total_sistema:.2f} GiB",
                    "disponivel_virtual": f"{disponivel:.2f} GiB",
                    "usada_virtual": f"{usado:.2f} GiB",
                    "percentual_virtual": int((usado / total_sistema) * 100) if total_sistema else 0
                }
        except Exception:
            pass

        # Fallback Disks
        if wmi:
            try:
                for disk in wmi.InstancesOf("Win32_DiskDrive"):
                    size_bytes = getattr(disk, 'Size', 0)
                    size_str = "N/A"
                    if size_bytes:
                        size_gb = size_bytes / 1e9
                        if size_gb >= 1000:
                            size_str = f"{size_gb / 1000:.2f} TB"
                        else:
                            size_str = f"{size_gb:.2f} GB"
                    
                    model_upper = getattr(disk, 'Model', '').upper()
                    disk_type = "SSD/HDD"
                    if "SSD" in model_upper or "NVME" in model_upper or "SA400" in model_upper or "SNV2S" in model_upper:
                        disk_type = "SSD"
                    elif "HDD" in model_upper or "WDC" in model_upper or "SEAGATE" in model_upper:
                        disk_type = "HD"

                    dados["disks"].append({
                        "model": getattr(disk, 'Model', 'Desconhecido').strip(),
                        "size": size_str,
                        "firmware": getattr(disk, 'FirmwareRevision', 'N/A').strip(),
                        "media_type": getattr(disk, 'MediaType', 'Desconhecido').strip(),
                        "bytes_sector": str(getattr(disk, 'BytesPerSector', 'N/A')),
                        "disk_type": disk_type
                    })
            except Exception:
                pass

    return dados

def obter_uso_tempo_real():
    # Retorna o uso de CPU, GPU e de RAM em tempo real
    # 1. USO DE GPU (nvidia-smi com fallback WMI)
    gpu_val = 0.0
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=1, creationflags=0x08000000
        )
        if res.returncode == 0 and res.stdout.strip():
            gpu_val = float(res.stdout.strip())
    except Exception:
        try:
            ps_gpu = "(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | Where-Object { $_.Name -like '*engtype_3D' } | Measure-Object -Property UtilizationPercentage -Sum).Sum"
            res = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_gpu],
                capture_output=True, text=True, timeout=1.5, creationflags=0x08000000
            )
            if res.returncode == 0 and res.stdout.strip():
                gpu_val = min(float(res.stdout.strip()), 100.0)
        except Exception:
            gpu_val = 0.0

    # 2. USO DE CPU E RAM (Via PowerShell em bloco único rápido)
    cpu_val = 0.0
    ram_data = {}
    ps_script = """
    $cpu = (Get-CimInstance Win32_Processor).LoadPercentage
    $os = Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory
    [PSCustomObject]@{
        CPU = $cpu
        OS = $os
    } | ConvertTo-Json
    """
    try:
        process = subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=0x08000000
        )
        stdout_bytes, stderr_bytes = process.communicate(input=ps_script.encode('utf-8'), timeout=2.5)
        
        stdout = ""
        if stdout_bytes:
            for enc in ['utf-8', 'cp1252', 'latin-1', 'cp850']:
                try:
                    stdout = stdout_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if not stdout:
                stdout = stdout_bytes.decode('utf-8', errors='replace')
                
        if process.returncode == 0 and stdout.strip():
            raw = json.loads(stdout)
            cpu_val = float(raw.get("CPU", 0.0) if raw.get("CPU") is not None else 0.0)
            
            os_info = raw.get("OS")
            if os_info:
                tot_ram = os_info.get("TotalVisibleMemorySize", 1)
                free_ram = os_info.get("FreePhysicalMemory", 0)
                used_ram = tot_ram - free_ram
                pct_ram = int((used_ram / tot_ram) * 100)
                
                tot_virt = os_info.get("TotalVirtualMemorySize", 1)
                free_virt = os_info.get("FreeVirtualMemory", 0)
                used_virt = tot_virt - free_virt
                pct_virt = int((used_virt / tot_virt) * 100)
                
                ram_data = {
                    "usado_fisica": f"{(used_ram / (1024*1024)):.2f} GiB",
                    "percentual_fisica": pct_ram,
                    "usada_virtual": f"{(used_virt / (1024*1024)):.2f} GiB",
                    "disponivel_virtual": f"{(free_virt / (1024*1024)):.2f} GiB",
                    "percentual_virtual": pct_virt
                }
    except Exception as e:
        print(f"Erro ao obter CPU/RAM real-time: {e}")

    # Fallback psutil local se WMI falhar
    if not ram_data and HAS_PSUTIL:
        try:
            mem_virtual = psutil.virtual_memory()
            swap = psutil.swap_memory()
            total_sistema = (mem_virtual.total + swap.total) / (1024 ** 3)
            disponivel = (mem_virtual.available + swap.free) / (1024 ** 3)
            usado = total_sistema - disponivel
            ram_data = {
                "usado_fisica": f"{(mem_virtual.used / (1024**3)):.2f} GiB",
                "percentual_fisica": mem_virtual.percent,
                "usada_virtual": f"{usado:.2f} GiB",
                "disponivel_virtual": f"{disponivel:.2f} GiB",
                "percentual_virtual": int((usado / total_sistema) * 100) if total_sistema else 0
            }
            if cpu_val == 0.0:
                cpu_val = psutil.cpu_percent()
        except Exception:
            pass

    return {
        "cpu": cpu_val,
        "gpu": gpu_val,
        "ram": ram_data
    }
