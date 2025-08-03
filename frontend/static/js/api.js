// frontend/static/js/api.js
// 백엔드 API 통신 래퍼

// API 기본 URL
const API_BASE_URL = '/api';

// HTTP 요청 헬퍼 함수
async function makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const requestOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, requestOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API 요청 실패:', error);
        throw error;
    }
}

// 이상형 데이터 제출
async function submitIdealTypeData(data) {
    try {
        const response = await makeRequest('/submit', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        
        if (response.success) {
            // 확률 계산 결과 표시
            displayCalculationResult(response);
        } else {
            showMessage(response.error || '처리 중 오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        showMessage('서버 연결에 실패했습니다.', 'error');
    } finally {
        hideLoading();
    }
}

// 확률 계산 결과 표시
function displayCalculationResult(response) {
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');
    
    if (resultContainer && resultContent) {
        // TODO: 실제 확률 계산 결과를 받아서 표시
        // 현재는 임시 데이터 사용
        
        const mockResult = {
            probability: Math.floor(Math.random() * 100),
            rarity_level: getRarityLevel(Math.floor(Math.random() * 100)),
            filters: response.data
        };
        
        resultContent.innerHTML = `
            <div class="result-item">
                <div class="probability-display">
                    <h4>매칭 확률</h4>
                    <div class="probability-number">${mockResult.probability}%</div>
                    <div class="rarity-badge ${getRarityClass(mockResult.rarity_level)}">
                        ${mockResult.rarity_level}
                    </div>
                </div>
                <div class="result-details">
                    <h5>입력한 조건</h5>
                    <ul>
                        <li>나이: ${mockResult.filters.age_range[0]}~${mockResult.filters.age_range[1]}세</li>
                        <li>지역: ${getLocationName(mockResult.filters.location)}</li>
                        <li>관심사: ${mockResult.filters.interests.join(', ')}</li>
                        ${mockResult.filters.style ? `<li>스타일: ${getStyleName(mockResult.filters.style)}</li>` : ''}
                        ${mockResult.filters.height ? `<li>키: ${mockResult.filters.height}</li>` : ''}
                    </ul>
                </div>
            </div>
        `;
        
        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

// 희귀도 레벨에 따른 클래스 반환
function getRarityClass(rarity) {
    switch (rarity) {
        case '매우 희귀':
            return 'rarity-legendary';
        case '희귀':
            return 'rarity-rare';
        case '보통':
            return 'rarity-common';
        case '흔함':
            return 'rarity-common';
        default:
            return 'rarity-common';
    }
}

// 희귀도 레벨 계산
function getRarityLevel(probability) {
    if (probability >= 80) return '매우 희귀';
    if (probability >= 60) return '희귀';
    if (probability >= 30) return '보통';
    return '흔함';
}

// 지역명 변환
function getLocationName(locationCode) {
    const locationMap = {
        'seoul': '서울',
        'busan': '부산',
        'daegu': '대구',
        'incheon': '인천',
        'gwangju': '광주',
        'daejeon': '대전',
        'ulsan': '울산',
        'sejong': '세종',
        'gyeonggi': '경기도',
        'gangwon': '강원도',
        'chungbuk': '충청북도',
        'chungnam': '충청남도',
        'jeonbuk': '전라북도',
        'jeonnam': '전라남도',
        'gyeongbuk': '경상북도',
        'gyeongnam': '경상남도',
        'jeju': '제주도'
    };
    
    return locationMap[locationCode] || locationCode;
}

// 스타일명 변환
function getStyleName(styleCode) {
    const styleMap = {
        'cute': '귀여운',
        'elegant': '우아한',
        'casual': '캐주얼',
        'sporty': '스포티',
        'classic': '클래식'
    };
    
    return styleMap[styleCode] || styleCode;
}

// 확률 계산 API 호출
async function calculateProbability(filters) {
    try {
        const response = await makeRequest('/calculate-probability', {
            method: 'POST',
            body: JSON.stringify(filters),
        });
        
        return response;
    } catch (error) {
        console.error('확률 계산 실패:', error);
        throw error;
    }
}

// 이미지 생성 API 호출
async function generateImage(filters) {
    try {
        const response = await makeRequest('/generate-image', {
            method: 'POST',
            body: JSON.stringify(filters),
        });
        
        return response;
    } catch (error) {
        console.error('이미지 생성 실패:', error);
        throw error;
    }
}

// 통계 데이터 조회
async function getStatistics() {
    try {
        const response = await makeRequest('/statistics', {
            method: 'GET',
        });
        
        return response;
    } catch (error) {
        console.error('통계 데이터 조회 실패:', error);
        throw error;
    }
} 