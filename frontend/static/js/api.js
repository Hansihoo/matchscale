// frontend/static/js/api.js
// 통계 기반 매칭 확률 계산 API 통신 래퍼

const API_BASE_URL = '/api';

/**
 * 이상형 조건 데이터를 서버에 제출하여 매칭 확률을 계산합니다.
 * 
 * @param {Object} formData - 이상형 조건 데이터
 * @returns {Promise<Object>} 매칭 확률 결과
 */
async function submitIdealTypeData(formData) {
    try {
        const response = await fetch(`${API_BASE_URL}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '서버 오류가 발생했습니다.');
        }

        if (!result.success) {
            throw new Error(result.error || '요청 처리에 실패했습니다.');
        }

        return result.result;

    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

/**
 * 통계 데이터 요약 정보를 조회합니다.
 * 
 * @returns {Promise<Object>} 통계 데이터 요약
 */
async function getStatisticsSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '서버 오류가 발생했습니다.');
        }

        return result.data;

    } catch (error) {
        console.error('통계 데이터 조회 오류:', error);
        throw error;
    }
}

/**
 * 사용 가능한 조건 옵션들을 조회합니다.
 * 
 * @returns {Promise<Object>} 조건별 옵션 데이터
 */
async function getAvailableConditions() {
    try {
        const response = await fetch(`${API_BASE_URL}/conditions`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '서버 오류가 발생했습니다.');
        }

        return result.data;

    } catch (error) {
        console.error('조건 옵션 조회 오류:', error);
        throw error;
    }
}

/**
 * 조건별 인구 비율을 계산합니다.
 * 
 * @param {Object} conditions - 선택된 조건들
 * @returns {Object} 조건별 비율 정보
 */
function calculateConditionRatios(conditions) {
    const ratios = {};
    
    // 키 조건 비율
    if (conditions.height) {
        const heightRatios = {
            '150-155': 8.5, '155-160': 15.2, '160-165': 25.8,
            '165-170': 28.4, '170-175': 15.1, '175-180': 5.8, '180-185': 1.2
        };
        ratios.height = heightRatios[conditions.height] || 0;
    }
    
    // 학력 조건 비율
    if (conditions.education) {
        const educationRatios = {
            'SKY': 3.2, '인서울': 12.5, '지거국': 8.7,
            '4년제': 45.3, '이하': 30.3
        };
        ratios.education = educationRatios[conditions.education] || 0;
    }
    
    // 연봉 조건 비율
    if (conditions.salary) {
        const salaryRatios = {
            '2000만원 이하': 35.2, '2000-3000만원': 28.7,
            '3000-4000만원': 18.9, '4000-5000만원': 10.2, '5000만원 이상': 7.0
        };
        ratios.salary = salaryRatios[conditions.salary] || 0;
    }
    
    // 직업 조건 비율
    if (conditions.job) {
        const jobRatios = {
            '전문직': 12.5, '공무원': 8.3, '공기업': 5.7, '그 외': 73.5
        };
        ratios.job = jobRatios[conditions.job] || 0;
    }
    
    // 지역 조건 비율
    if (conditions.location) {
        const locationRatios = {
            '수도권': 45.8, '지방광역시': 28.9, '기타': 25.3
        };
        ratios.location = locationRatios[conditions.location] || 0;
    }
    
    return ratios;
}

/**
 * 전체 매칭 확률을 계산합니다.
 * 
 * @param {Object} conditionRatios - 조건별 비율
 * @returns {number} 전체 매칭 확률 (%)
 */
function calculateTotalProbability(conditionRatios) {
    if (Object.keys(conditionRatios).length === 0) {
        return 100.0;
    }
    
    let totalProbability = 100.0;
    
    Object.values(conditionRatios).forEach(ratio => {
        totalProbability *= (ratio / 100);
    });
    
    return Math.round(totalProbability * 100) / 100;
}

/**
 * 확률에 따른 희귀도 레벨을 반환합니다.
 * 
 * @param {number} probability - 매칭 확률
 * @returns {string} 희귀도 레벨
 */
function getRarityLevel(probability) {
    if (probability >= 10.0) return '매우 흔함';
    if (probability >= 5.0) return '흔함';
    if (probability >= 2.0) return '보통';
    if (probability >= 0.5) return '희귀';
    if (probability >= 0.1) return '매우 희귀';
    return '극히 희귀';
}

// 전역 함수로 노출
window.submitIdealTypeData = submitIdealTypeData;
window.getStatisticsSummary = getStatisticsSummary;
window.getAvailableConditions = getAvailableConditions;
window.calculateConditionRatios = calculateConditionRatios;
window.calculateTotalProbability = calculateTotalProbability;
window.getRarityLevel = getRarityLevel; 