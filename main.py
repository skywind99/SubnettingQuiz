import streamlit as st
import ipaddress
import matplotlib.pyplot as plt
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="C 클래스 서브네팅 계산기", layout="wide")
st.title("🧮 C 클래스 서브네팅 계산기")

# 입력
ip_input = st.text_input("IP 주소 (예: 192.168.1.0)", value="192.168.1.0")
prefix_input = st.slider("프리픽스 (/CIDR)", min_value=24, max_value=30, value=26)

try:
    network = ipaddress.ip_network(f"{ip_input}/{prefix_input}", strict=False)
    total_ips = network.num_addresses
    usable_hosts = max(total_ips - 2, 0)
    subnet_size = 2 ** (32 - prefix_input)
    subnet_count = 256 // subnet_size

    st.subheader("📋 서브넷 요약")
    st.write(f"- 서브넷 마스크: {network.netmask}")
    st.write(f"- 총 IP 수: {total_ips}개")
    st.write(f"- 유효 호스트 수: {usable_hosts}개")
    st.write(f"- 서브넷 수 (C 클래스 기준): {subnet_count}개")

    # 서브넷 리스트 만들기
    subnet_list = []
    for i in range(subnet_count):
        net_addr = ipaddress.ip_network(f"{ip_input}/{prefix_input}", strict=False)
        net_addr = ipaddress.ip_network((int(net_addr.network_address) + i * subnet_size, prefix_input))
        subnet_list.append([
            i + 1,
            str(net_addr.network_address),
            str(list(net_addr.hosts())[0]) if usable_hosts > 0 else '-',
            str(list(net_addr.hosts())[-1]) if usable_hosts > 0 else '-',
            str(net_addr.broadcast_address)
        ])

    df = pd.DataFrame(subnet_list, columns=["서브넷 번호", "네트워크 주소", "첫 호스트", "마지막 호스트", "브로드캐스트"])
    st.dataframe(df, use_container_width=True)

    # 시각화 (네트워크 구조)
    fig, ax = plt.subplots(figsize=(10, 1 + 0.5 * min(subnet_count, 10)))
    for i, row in df.iterrows():
        ax.broken_barh([(i * 10, 9)], (0, 5), facecolors='tab:blue')
        ax.text(i * 10 + 1, 2.5, f"{row['네트워크 주소']}\n~\n{row['브로드캐스트']}", va='center', fontsize=8, color='white')
    ax.set_xlim(0, max(10 * subnet_count, 100))
    ax.axis('off')
    st.subheader("📊 서브넷 시각화")
    st.pyplot(fig)

except ValueError:
    st.error("올바른 IP 주소를 입력해주세요. 예: 192.168.1.0")
