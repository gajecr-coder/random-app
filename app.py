import streamlit as st
import json
import os
import uuid
import base64
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="미사고등학교 분실물 알리미 | 당근 스타일",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 공용 데이터 및 이미지 경로 설정 (모든 접속자 공유)
DATA_DIR = "lost_found_data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")
DATA_FILE = os.path.join(DATA_DIR, "posts.json")
os.makedirs(IMAGE_DIR, exist_ok=True)


# --- 유틸리티 함수 ---
def get_base64_image(image_path):
    """로컬 이미지를 HTML 삽입용 Base64 문자열로 변환"""
    if not image_path or not os.path.exists(image_path):
        return None
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/{ext};base64,{encoded}"


def get_school_logo_b64():
    """저장된 미사고등학교 로고 파일 자동 탐색"""
    candidates = ["misa_logo.jpg", "misa_logo.png", "misa_logo.jpeg", "image_5cf0b4.jpg"]
    for filename in candidates:
        if os.path.exists(filename):
            return get_base64_image(filename)
    return None


def load_posts():
    """저장된 모든 게시물 불러오기"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_posts(posts):
    """게시물 목록 JSON 저장"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)


def add_post(post_data, uploaded_image):
    """새 게시물 및 사진 저장"""
    posts = load_posts()
    post_id = uuid.uuid4().hex
    image_path = None

    if uploaded_image is not None:
        ext = os.path.splitext(uploaded_image.name)[1].lower()
        image_filename = f"{post_id}{ext}"
        image_path = os.path.join(IMAGE_DIR, image_filename)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

    new_post = {
        "id": post_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": image_path,
        **post_data
    }
    posts.insert(0, new_post)
    save_posts(posts)


def delete_post(post_id):
    """게시물 및 연결된 사진 파일 삭제"""
    posts = load_posts()
    updated_posts = []
    for post in posts:
        if post["id"] == post_id:
            if post.get("image_path") and os.path.exists(post["image_path"]):
                try:
                    os.remove(post["image_path"])
                except OSError:
                    pass
        else:
            updated_posts.append(post)
    save_posts(updated_posts)


def format_datetime_str(date_val, time_val):
    """날짜/시간 포맷팅"""
    parts = []
    if date_val:
        parts.append(date_val.strftime("%Y년 %m월 %d일"))
    if time_val:
        parts.append(time_val.strftime("%H시 %M분"))
    return " ".join(parts) if parts else "미상 / 해당 없음"


def get_relative_time(created_at_str):
    """당근마켓 스타일 상대 시간 표시 (예: 방금 전, 12분 전)"""
    try:
        created = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - created
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "방금 전"
        elif seconds < 3600:
            return f"{seconds // 60}분 전"
        elif seconds < 86400:
            return f"{seconds // 3600}시간 전"
        else:
            return f"{seconds // 86400}일 전"
    except Exception:
        return created_at_str


# 3. 당근마켓 벤치마킹 커스텀 CSS
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        color: #212124;
    }

    /* Streamlit 기본 상단 여백 및 데코레이션 정리 */
    .block-container {
        max-width: 760px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 4rem !important;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* 당근마켓 상단 헤더 바 */
    .karrot-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 4px 16px 4px;
        border-bottom: 1px solid #EAEDEF;
        margin-bottom: 16px;
        background-color: #FFFFFF;
    }
    .karrot-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .karrot-logo-img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 1.5px solid #EAEDEF;
        background: #FFF;
    }
    .karrot-logo-fallback {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #0028D4;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 13px;
    }
    .karrot-school-title {
        font-size: 20px;
        font-weight: 800;
        color: #212124;
        letter-spacing: -0.4px;
        line-height: 1.2;
    }
    .karrot-school-sub {
        font-size: 12.5px;
        font-weight: 600;
        color: #FF6F0F;
        margin-top: 2px;
    }

    /* 당근 시그니처 오렌지 버튼 스타일 */
    div.stButton > button[kind="primary"] {
        background-color: #FF6F0F !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem !important;
        transition: background-color 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #E56008 !important;
    }

    /* 보조 버튼 스타일 */
    div.stButton > button[kind="secondary"] {
        background-color: #F2F3F6 !important;
        color: #212124 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #E6E8EC !important;
    }

    /* 당근 피드 아이템 카드 */
    .karrot-feed-item {
        display: flex;
        gap: 16px;
        padding: 16px 4px;
        border-bottom: 1px solid #EAEDEF;
        align-items: flex-start;
    }
    .karrot-thumb {
        width: 128px;
        height: 128px;
        min-width: 128px;
        border-radius: 12px;
        object-fit: cover;
        border: 1px solid #EAEDEF;
        background-color: #F8F9FA;
    }
    .karrot-thumb-empty {
        width: 128px;
        height: 128px;
        min-width: 128px;
        border-radius: 12px;
        background-color: #F2F3F6;
        border: 1px solid #EAEDEF;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #868B94;
        font-size: 12px;
        font-weight: 500;
    }
    .karrot-item-body {
        flex: 1;
        min-width: 0;
    }
    .karrot-item-title {
        font-size: 16.5px;
        font-weight: 600;
        color: #212124;
        margin-bottom: 4px;
        line-height: 1.35;
        word-break: keep-all;
    }
    .karrot-item-meta {
        font-size: 13px;
        color: #868B94;
        margin-bottom: 8px;
    }
    .karrot-badge-found {
        display: inline-block;
        background-color: #E8F7EE;
        color: #16A34A;
        font-size: 11.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 5px;
        margin-right: 6px;
        vertical-align: middle;
    }
    .karrot-badge-lost {
        display: inline-block;
        background-color: #FFF1E6;
        color: #FF6F0F;
        font-size: 11.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 5px;
        margin-right: 6px;
        vertical-align: middle;
    }
    .karrot-storage-line {
        font-size: 14.5px;
        font-weight: 700;
        color: #212124;
        margin-bottom: 6px;
    }
    .karrot-preview-desc {
        font-size: 13px;
        color: #4D5159;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.45;
    }

    /* 상세 페이지 스타일 */
    .detail-profile-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid #EAEDEF;
        margin-bottom: 18px;
    }
    .detail-info-box {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 16px 18px;
        margin: 14px 0;
        border: 1px solid #EAEDEF;
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid #ECEEF0;
        font-size: 14px;
    }
    .detail-row:last-child {
        border-bottom: none;
    }
    .detail-label {
        color: #868B94;
        font-weight: 500;
    }
    .detail-val {
        color: #212124;
        font-weight: 600;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 4. 화면 상태 관리 (feed: 목록, write: 글쓰기, detail: 상세보기)
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "feed"
if "selected_post_id" not in st.session_state:
    st.session_state.selected_post_id = None

logo_b64 = get_school_logo_b64()
logo_html = (
    f'<img src="{logo_b64}" class="karrot-logo-img" alt="미사고등학교 로고">'
    if logo_b64
    else '<div class="karrot-logo-fallback">미사고</div>'
)

# ==========================================================
# 상단 공통 당근마켓 스타일 헤더
# ==========================================================
header_left, header_right = st.columns([3.2, 1.3])
with header_left:
    st.markdown(f"""
    <div class="karrot-brand">
        {logo_html}
        <div>
            <div class="karrot-school-title">미사고등학교 ▾</div>
            <div class="karrot-school-sub">우리 학교 분실물 · 습득물 알리미</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_right:
    st.write("")
    if st.session_state.page_mode == "feed":
        if st.button("＋ 글쓰기", type="primary", use_container_width=True):
            st.session_state.page_mode = "write"
            st.rerun()
    else:
        if st.button("← 목록으로", type="secondary", use_container_width=True):
            st.session_state.page_mode = "feed"
            st.session_state.selected_post_id = None
            st.rerun()

st.markdown('<div style="border-bottom: 1px solid #EAEDEF; margin-top: -8px; margin-bottom: 16px;"></div>', unsafe_allow_html=True)


# ==========================================================
# 뷰 1: 당근마켓 피드형 분실물 목록 화면
# ==========================================================
if st.session_state.page_mode == "feed":
    # 검색창 + 새로고침
    s_col, r_col = st.columns([4.5, 1])
    with s_col:
        search_keyword = st.text_input(
            "검색",
            placeholder="🔍 미사고에서 잃어버리거나 주운 물건을 검색해보세요",
            label_visibility="collapsed"
        )
    with r_col:
        if st.button("새로고침", type="secondary", use_container_width=True):
            st.rerun()

    # 당근 스타일 카테고리 필터 라디오
    filter_type = st.radio(
        "필터",
        ["전체", "🟢 습득물 (주웠어요)", "🟠 분실물 (잃어버렸어요)"],
        horizontal=True,
        label_visibility="collapsed"
    )

    posts = load_posts()
    filtered_posts = []

    for p in posts:
        p_type = p.get("post_type", "")
        if "습득물" in filter_type and "습득물" not in p_type:
            continue
        if "분실물" in filter_type and "분실물" not in p_type:
            continue
        if search_keyword.strip():
            kw = search_keyword.strip().lower()
            searchable = " ".join([
                p.get("item_name", ""),
                p.get("features", ""),
                p.get("last_lost_location", ""),
                p.get("found_location", ""),
                p.get("storage_location", "")
            ]).lower()
            if kw not in searchable:
                continue
        filtered_posts.append(p)

    st.caption(f"등록된 게시글 **{len(filtered_posts)}개** · 누구나 자유롭게 등록하고 삭제할 수 있습니다.")

    if not filtered_posts:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #868B94;">
            <div style="font-size: 38px; margin-bottom: 10px;">🥕</div>
            <div style="font-size: 16px; font-weight: 600; color: #212124;">등록된 분실물·습득물이 없어요</div>
            <div style="font-size: 13.5px; margin-top: 4px;">우측 상단의 <b>+ 글쓰기</b> 버튼을 눌러 첫 소식을 올려보세요!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for post in filtered_posts:
            is_found = "습득물" in post.get("post_type", "")
            badge_html = (
                '<span class="karrot-badge-found">주웠어요</span>'
                if is_found
                else '<span class="karrot-badge-lost">찾아요</span>'
            )

            # 썸네일 처리
            img_b64 = get_base64_image(post.get("image_path"))
            if img_b64:
                thumb_html = f'<img src="{img_b64}" class="karrot-thumb">'
            else:
                thumb_html = '<div class="karrot-thumb-empty">📷<br>사진 없음</div>'

            # 장소 요약 (발견 장소 또는 최종 분실 위치)
            loc_summary = (
                post.get("found_location")
                if is_found and post.get("found_location")
                else post.get("last_lost_location") or post.get("found_location") or "교내 위치 미상"
            )
            rel_time = get_relative_time(post.get("created_at", ""))
            storage_text = post.get("storage_location") or "보관 위치 미지정"

            # 당근마켓 피드 카드 렌더링
            st.markdown(f"""
            <div class="karrot-feed-item">
                {thumb_html}
                <div class="karrot-item-body">
                    <div class="karrot-item-title">{badge_html}{post.get('item_name', '물품명 없음')}</div>
                    <div class="karrot-item-meta">{loc_summary} · {rel_time}</div>
                    <div class="karrot-storage-line">📦 보관: {storage_text}</div>
                    <div class="karrot-preview-desc">{post.get('features', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 카드 하단 액션 버튼 (상세보기 / 즉시 삭제)
            b_space, b_detail, b_del = st.columns([3.2, 1.1, 0.9])
            with b_detail:
                if st.button("상세보기", key=f"view_{post['id']}", type="secondary", use_container_width=True):
                    st.session_state.selected_post_id = post["id"]
                    st.session_state.page_mode = "detail"
                    st.rerun()
            with b_del:
                if st.button("삭제", key=f"del_{post['id']}", type="secondary", use_container_width=True):
                    delete_post(post["id"])
                    st.rerun()


# ==========================================================
# 뷰 2: 당근마켓 상세 페이지 화면
# ==========================================================
elif st.session_state.page_mode == "detail":
    posts = load_posts()
    target_post = next((p for p in posts if p["id"] == st.session_state.selected_post_id), None)

    if not target_post:
        st.warning("삭제되었거나 존재하지 않는 게시물입니다.")
        st.session_state.page_mode = "feed"
        st.rerun()

    # 상단 물품 이미지
    if target_post.get("image_path") and os.path.exists(target_post["image_path"]):
        st.image(target_post["image_path"], use_container_width=True)

    # 당근마켓 스타일 작성자(학교) 프로필 바
    st.markdown(f"""
    <div class="detail-profile-bar">
        <div style="display:flex; align-items:center; gap:10px;">
            {logo_html}
            <div>
                <div style="font-weight:700; font-size:15px; color:#212124;">미사고등학교 학생·교직원</div>
                <div style="font-size:12.5px; color:#868B94;">등록일시: {target_post.get('created_at', '-')}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <span style="color:#FF6F0F; font-weight:800; font-size:15px;">36.5°C 😊</span>
            <div style="font-size:11px; color:#868B94;">미사 매너온도</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    is_found = "습득물" in target_post.get("post_type", "")
    badge_text = "🟢 습득물 (주웠어요)" if is_found else "🟠 분실물 (잃어버렸어요)"

    st.caption(badge_text)
    st.markdown(f"### {target_post.get('item_name', '')}")
    st.markdown(f"**📦 현재 보관 위치: `{target_post.get('storage_location') or '미지정'}`**")

    # 모든 필수 세부 항목 표기
    st.markdown(f"""
    <div class="detail-info-box">
        <div class="detail-row">
            <span class="detail-label">📍 기억나는 최종 분실 위치</span>
            <span class="detail-val">{target_post.get('last_lost_location') or '미상 / 해당 없음'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">🕒 기억나는 최종 분실 일시</span>
            <span class="detail-val">{target_post.get('last_lost_datetime') or '미상 / 해당 없음'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">🔍 발견 장소</span>
            <span class="detail-val">{target_post.get('found_location') or '미상 / 해당 없음'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">📅 발견 날짜 및 시간</span>
            <span class="detail-val">{target_post.get('found_datetime') or '미상 / 해당 없음'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">🏢 현재 보관 위치</span>
            <span class="detail-val" style="color:#FF6F0F;">{target_post.get('storage_location') or '미지정'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📝 분실물 주요 특징")
    st.write(target_post.get("features", "기재된 특징이 없습니다."))

    st.divider()
    col_back, col_delete = st.columns([3, 1.2])
    with col_delete:
        if st.button("🗑️ 게시물 삭제하기", type="primary", use_container_width=True):
            delete_post(target_post["id"])
            st.session_state.page_mode = "feed"
            st.session_state.selected_post_id = None
            st.rerun()


# ==========================================================
# 뷰 3: 당근마켓 "+ 글쓰기" 등록 화면
# ==========================================================
elif st.session_state.page_mode == "write":
    st.markdown("### 🥕 미사고 분실물 · 습득물 글쓰기")
    st.caption("모르는 항목이나 해당 없는 항목은 비워두셔도 등록됩니다.")

    with st.form("karrot_write_form", clear_on_submit=True):
        uploaded_image = st.file_uploader(
            "📷 분실물 사진 올리기 (선택)",
            type=["png", "jpg", "jpeg", "webp"]
        )

        post_type = st.radio(
            "게시글 유형 *",
            ["🟢 습득물 (주웠어요)", "🟠 분실물 (잃어버렸어요)"],
            horizontal=True
        )

        item_name = st.text_input(
            "글 제목 (물품명) *",
            placeholder="예: 검정색 에어팟 프로 케이스, 파란색 3단 우산"
        )

        storage_location = st.text_input(
            "📦 현재 보관 위치",
            placeholder="예: 본관 2층 교무실 분실물 함 / 학생회실 / 본인 보관 중"
        )

        st.markdown("---")
        st.markdown("**📍 분실 정보 (잃어버린 경우 작성)**")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            last_lost_location = st.text_input(
                "기억나는 최종 분실 위치",
                placeholder="예: 본관 3층 2반 교실 뒷문"
            )
        with c2:
            last_lost_date = st.date_input("최종 분실 날짜", value=None)
        with c3:
            last_lost_time = st.time_input("최종 분실 시간", value=None)

        st.markdown("**🔍 습득 정보 (주운 경우 작성)**")
        c4, c5, c6 = st.columns([2, 1, 1])
        with c4:
            found_location = st.text_input(
                "발견 장소",
                placeholder="예: 급식실 앞 복도 정수기 옆"
            )
        with c5:
            found_date = st.date_input("발견 날짜", value=None)
        with c6:
            found_time = st.time_input("발견 시간", value=None)

        st.markdown("---")
        features = st.text_area(
            "📝 해당 분실물의 주요 특징들 *",
            placeholder="미사고 학생·선생님이 알아볼 수 있도록 색상, 브랜드, 스크래치, 키링, 이름표 등 특징을 자세히 적어주세요.",
            height=130
        )

        submitted = st.form_submit_button("작성 완료", type="primary", use_container_width=True)

        if submitted:
            if not item_name.strip() or not features.strip():
                st.error("⚠️ '물품명'과 '주요 특징들'을 입력해 주세요.")
            else:
                post_data = {
                    "post_type": post_type,
                    "item_name": item_name.strip(),
                    "last_lost_location": last_lost_location.strip(),
                    "last_lost_datetime": format_datetime_str(last_lost_date, last_lost_time),
                    "found_location": found_location.strip(),
                    "found_datetime": format_datetime_str(found_date, found_time),
                    "storage_location": storage_location.strip(),
                    "features": features.strip(),
                }
                add_post(post_data, uploaded_image)
                st.session_state.page_mode = "feed"
                st.rerun()
