import socket
import ssl
from datetime import datetime
import requests
from urllib.parse import urlparse
from tabulate import tabulate  # 用于美化输出

def get_ssl_certificate_info(domain):
    """获取指定域名的SSL证书信息"""
    port = 443  # HTTPS默认端口
    ctx = ssl.create_default_context()
    
    try:
        with socket.create_connection((domain, port)) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:
        print(f"获取证书信息失败: {e}")
        return None

def parse_certificate_info(cert):
    """解析证书信息"""
    if not cert:
        return {}
    
    certificate_info = {
        "主题": cert.get('subject', ''),
        "颁发者": cert.get('issuer', ''),
        "有效期开始": cert.get('notBefore', ''),
        "有效期结束": cert.get('notAfter', ''),
        "签名算法": cert.get('signatureAlgorithm', ''),
        "版本": cert.get('version', ''),
        "序列号": cert.get('serialNumber', '')
    }
    
    return certificate_info

def associate_other_websites(cert):
    """关联查询其他使用相同证书的网站"""
    if not cert:
        return []
    
    # 提取证书的序列号
    serial_number = cert.get('serialNumber', '')
    
    # 使用CRT.SH的API查询证书透明度日志
    try:
        response = requests.get(f"https://crt.sh/?q={serial_number}")
        response.raise_for_status()
        results = response.json()
        
        # 提取关联的网站域名
        associated_websites = []
        for result in results:
            associated_websites.append(result['name_value'])
        
        return list(set(associated_websites))  # 去重
    except Exception as e:
        print(f"查询证书透明度日志失败: {e}")
        return []

def save_to_file(info, associated_websites):
    """将信息保存到out.txt文件"""
    with open("out.txt", "w") as f:
        f.write("证书信息:\n")
        for key, value in info.items():
            f.write(f"{key}: {value}\n")
        
        f.write("\n关联的其他网站:\n")
        for site in associated_websites:
            f.write(f"{site}\n")

def print_beautiful_output(info, associated_websites):
    """美化输出"""
    print("\n证书信息:")
    certificate_table = []
    for key, value in info.items():
        certificate_table.append([key, value])
    print(tabulate(certificate_table, headers=["字段", "值"], tablefmt="grid"))
    
    print("\n关联的其他网站:")
    print(tabulate([[site] for site in associated_websites], headers=["网站"], tablefmt="grid"))

def main():
    domain = input("请输入要查询的网站域名（例如：www.example.com）: ")
    
    # 获取证书信息
    cert = get_ssl_certificate_info(domain)
    
    if not cert:
        print("未能获取证书信息，请检查域名是否正确或网络连接。")
        return
    
    # 解析证书信息
    certificate_info = parse_certificate_info(cert)
    
    # 关联查询其他网站
    associated_websites = associate_other_websites(cert)
    
    # 美化输出
    print_beautiful_output(certificate_info, associated_websites)
    
    # 保存到文件
    save_to_file(certificate_info, associated_websites)
    
    print("\n证书信息及关联网站已保存到out.txt文件中。")

if __name__ == "__main__":
    main()