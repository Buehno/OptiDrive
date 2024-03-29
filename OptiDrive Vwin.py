import pandas as pd
import sqlite3
import platform
import psutil
import cpuinfo
import GPUtil
import wmi
import pywintypes
import requests
import os
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk


def criar_tabela():
    data = sqlite3.connect("database.db")
    cursor = data.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infos (
            cpu TEXT,
            ram TEXT,
            memoria TEXT,
            mother_board TEXT,
            fonte TEXT,
            sistem TEXT,
            status TEXT
        )
    ''')
    data.commit()
    data.close()


def check_disk_health():
    partitions = psutil.disk_partitions()

    for partition in partitions:

        disk_usage = psutil.disk_usage(partition.mountpoint)
        health_status = "Saudável"

        if hasattr(psutil, 'sensors'):
            try:
                # Verifica o atributo SMART
                smart_info = psutil.sensors_smart_values(partition.device)
                if 'assessment' in smart_info:
                    assessment = smart_info['assessment']
                    if assessment == 'Risco':
                        health_status = "Risco"
                    elif assessment == 'Crítico':
                        health_status = "Crítico"
            except AttributeError:
                pass

        print(f"Partição: {partition.device}")
        print(f"Status de Saúde: {health_status}")


def is_windows_64bit():
    # Verifica se a variável de ambiente 'ProgramFiles(x86)' existe. Ela só existe em sistemas de 64 bits.
    return 'ProgramFiles(x86)' in os.environ


win = ("64 bits") if is_windows_64bit() else ("32 bits")

# Informações da Memória Interna


def get_memory():
    partitions = psutil.disk_partitions()
    disk_info = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            # Capacidade total do disco em GB
            total_space_gb = usage.total / (1024**3)
            used_space_gb = usage.used / (1024**3)    # Espaço utilizado em GB

            disk_info.append(f"Disco {partition.device}:")
            disk_info.append(f"  Capacidade Total: {total_space_gb:.2f} GB")
            disk_info.append(f"  Espaço Utilizado: {used_space_gb:.2f} GB")
            disk_info.append("\n")
        except Exception as e:
            disk_info.append(
                f"Erro ao obter informações do disco {partition.device}: {str(e)}")

    return "\n".join(disk_info)


def get_ram():
    ram = psutil.virtual_memory()
    total_ram_gb = ram.total / (1024**3)  # Capacidade total de RAM em GB
    used_ram_gb = ram.used / (1024**3)    # Quantidade de RAM em uso em GB
    percent_used = ram.percent            # Porcentagem de RAM em uso

    return f"Capacidade Total de RAM: {total_ram_gb:.2f} GB, RAM em Uso: {used_ram_gb:.2f} GB, Porcentagem de Uso: {percent_used:.2f}%"

# Informações da GPU


def get_gpu():
    try:
        GPUs = GPUtil.getGPUs()
        gpu_info = []
        if not GPUs:
            return ["Nenhuma GPU encontrada."]
        for gpu in GPUs:
            gpu_info.append(f"GPU: {gpu.name}, Uso GPU: {gpu.gpu}%")
        return gpu_info
    except Exception as e:
        return [f"Erro ao obter informações da GPU..."]

# Informações da CPU


def get_cpu():
    info = cpuinfo.get_cpu_info()
    return f"CPU: {info['brand_raw']}"

# Informações da Placa-mãe


def get_motherboard():
    w = wmi.WMI()
    motherboard = w.Win32_BaseBoard()[0]
    return f"Placa-mãe: {motherboard.Product}"

# Informações da Fonte de Alimentação


def get_power_supply():
    try:
        w = wmi.WMI()
        power_supplies = w.query("SELECT * FROM Win32_PowerSupply")
        if power_supplies:
            return f"Fonte de Alimentação: {power_supplies[0].Name}"
        else:
            return "Fonte de Alimentação não encontrada"
    except Exception as e:
        return f"Erro ao obter informações da fonte de alimentação..."


def cadastro():

    print("\nAqui estão suas informações:")
    print(get_memory())
    check_disk_health()  # Chame check_disk_health aqui, fora do loop
    print(get_ram())
    print(get_cpu())
    print(get_motherboard())
    print(f"Sistema operando em: {win}")
    gpu_info = get_gpu()
    if gpu_info:
        for info in gpu_info:
            print(info)
    else:
        print("Nenhuma GPU encontrada.")
    print(get_power_supply())

    data = sqlite3.connect("database.db")
    cursor = data.cursor()
    cursor.execute("INSERT INTO infos (cpu, ram, memoria, status, mother_board, fonte, sistem) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (get_cpu(), get_ram(), get_memory(), "status", get_motherboard(), get_power_supply(), win))
    data.commit()
    data.close()
    print("Inscrição realizada com sucesso!")


def consultar_melhoria():
    print(f"certo, vamos pelo começo. Vejo que seu sistema é um {win}")
    if win == "64 bits":
        print("Certo, então você está com uma máquina que possui a capacidade de até 32GB de memória RAM. Podemos começar por isso, estou gerando uma sugestão de compra com o melhor custo-benefício para isso.")
    elif win == "32 bits":
        print("Certo, então você está com uma máquina que possui a capacidade de até 8GB de memória RAM. Podemos começar por isso, estou gerando uma sugestão de compra com o melhor custo-benefício para isso.")
    else:
        win = input(
            "Parece que não consegui pegar os seus dados corretamente para sugestão. Poderia me informar quantos bits seria sua máquina? [ex: 32 bits, 64 bits]")
        data = sqlite3.connect("database.db")
        cursor = data.cursor()
        cursor.execute("INSERT INTO infos (sistem) VALUES (?)",
                       (win,))
        data.commit()
        data.close()


def menu():
    criar_tabela()
    while True:
        print("\nMenu:")
        print("1. Registrar máquina")
        print("2. Consultar melhoria (beta)")
        print("3. Melhoria por orçamento")
        print("4. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            cadastro()
        elif escolha == "2":
            consultar_melhoria()
        elif escolha == "4":
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()

janela = tk.Tk()  # Corrigir a chamada para a classe Tk()
janela.title("OPTIDRIVE")  # Corrigir a chamada para o método title()
janela.mainloop()
