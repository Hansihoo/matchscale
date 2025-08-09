// frontend/static/js/main.js
// 통계 기반 이상형 매칭 확률 계산 - 사용자 입력 이벤트 핸들링

document.addEventListener('DOMContentLoaded', function() {
    // 페이지 로드 시 초기화
    initializePage();
});

function initializePage() {
    // 폼 제출 이벤트 리스너 등록
    setupFormSubmission();
    
    // 입력 필드 유효성 검사
    setupValidation();
    
    // 조건 선택 시 실시간 요약 업데이트
    setupConditionSummary();
}

function setupFormSubmission() {
    const form = document.getElementById('idealTypeForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 폼 데이터 수집
            const formData = collectFormData();
            
            // 데이터 유효성 검사
            if (!validateFormData(formData)) {
                return;
            }
            
            // 로딩 상태 표시
            showLoading();
            
            // API 호출
            submitIdealTypeData(formData);
        });
    }
}

function collectFormData() {
    return {
        gender: document.getElementById('gender').value,
        age_range: (function() {
            const minEl = document.getElementById('ageMin');
            const maxEl = document.getElementById('ageMax');
            if (!minEl || !maxEl) return null;
            const min = parseInt(minEl.value);
            const max = parseInt(maxEl.value);
            if (Number.isInteger(min) && Number.isInteger(max)) return [min, max];
            return null;
        })(),
        height: document.getElementById('height').value,
        education: document.getElementById('education').value,
        salary: document.getElementById('salary').value,
        job: document.getElementById('job').value,
        location: document.getElementById('location').value,
        marital_status: document.getElementById('marital_status').value,
        smoking: document.getElementById('smoking').value
    };
}

function validateFormData(data) {
    // 필수 필드 검증
    if (!data.gender) {
        showMessage('성별을 선택해주세요.', 'error');
        return false;
    }
    
    // 나이 범위 검증
    if (data.age_range) {
        if (data.age_range[0] < 18 || data.age_range[1] > 100 || data.age_range[0] >= data.age_range[1]) {
            showMessage('올바른 나이 범위를 입력해주세요 (18-100세, 최소 < 최대).', 'error');
            return false;
        }
    }
    
    // 최소 하나의 조건은 선택되어야 함
    const hasCondition = data.height || data.education || data.salary || 
                        data.job || data.location || data.marital_status || data.smoking;
    
    if (!hasCondition) {
        showMessage('최소 하나의 조건을 선택해주세요.', 'error');
        return false;
    }
    
    return true;
}

function setupValidation() {
    // 나이 입력 필드 실시간 검증
    const ageMin = document.getElementById('ageMin');
    const ageMax = document.getElementById('ageMax');
    
    if (ageMin && ageMax) {
        ageMin.addEventListener('input', validateAgeRange);
        ageMax.addEventListener('input', validateAgeRange);
    }
}

function validateAgeRange() {
    const ageMin = parseInt(document.getElementById('ageMin').value);
    const ageMax = parseInt(document.getElementById('ageMax').value);
    
    if (Number.isInteger(ageMin) && Number.isInteger(ageMax) && ageMin >= ageMax) {
        document.getElementById('ageMax').setCustomValidity('최대 나이는 최소 나이보다 커야 합니다.');
    } else {
        document.getElementById('ageMax').setCustomValidity('');
    }
}

function setupConditionSummary() {
    // 모든 select 요소에 변경 이벤트 리스너 추가
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', updateConditionsSummary);
    });
}

function updateConditionsSummary() {
    const selectedConditions = {};
    const selects = document.querySelectorAll('select');
    
    selects.forEach(select => {
        if (select.value) {
            const option = select.options[select.selectedIndex];
            selectedConditions[select.name] = {
                label: option.text,
                ratio: option.dataset.ratio
            };
        }
    });
    
    const summaryDiv = document.getElementById('conditionsSummary');
    const container = document.getElementById('selectedConditions');
    
    if (Object.keys(selectedConditions).length > 0) {
        let summaryHTML = '<div class="conditions-grid">';
        Object.keys(selectedConditions).forEach(key => {
            const condition = selectedConditions[key];
            const ratioText = condition.ratio ? ` (${condition.ratio}%)` : '';
            summaryHTML += `
                <div class="condition-item">
                    <strong>${getConditionLabel(key)}:</strong> 
                    ${condition.label}${ratioText}
                </div>
            `;
        });
        summaryHTML += '</div>';
        
        summaryDiv.innerHTML = summaryHTML;
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

function getConditionLabel(key) {
    const labels = {
        'gender': '성별',
        'age_range': '나이',
        'height': '키',
        'education': '학력',
        'salary': '연봉',
        'job': '직업',
        'location': '지역',
        'marital_status': '혼인여부',
        'smoking': '흡연여부'
    };
    return labels[key] || key;
}

function showLoading() {
    const submitBtn = document.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.textContent = '계산 중...';
        submitBtn.disabled = true;
    }
}

function hideLoading() {
    const submitBtn = document.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.textContent = '매칭 확률 계산하기';
        submitBtn.disabled = false;
    }
}

function showMessage(message, type = 'info') {
    // 메시지 표시 로직
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // TODO: 실제 UI에 메시지 표시 구현
    // 예: 토스트 메시지, 알림창 등
}

function displayResult(result) {
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');
    
    if (resultContainer && resultContent) {
        let resultHTML = `
            <div class="result-main">
                <h4>매칭 확률: ${result.probability}%</h4>
                <p class="rarity-level">희귀도: ${result.rarity_level}</p>
            </div>
        `;
        
        // 조건별 비율 상세 정보
        if (result.condition_ratios && Object.keys(result.condition_ratios).length > 0) {
            resultHTML += '<div class="condition-details"><h5>조건별 인구 비율:</h5><ul>';
            Object.keys(result.condition_ratios).forEach(condition => {
                const ratio = result.condition_ratios[condition];
                resultHTML += `<li><strong>${getConditionLabel(condition)}:</strong> ${ratio}%</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        // 통계 정보
        resultHTML += `
            <div class="stats-info">
                <p>적용된 조건 수: ${result.total_conditions}개</p>
                <p>데이터 출처: 통계청, 고용노동부 등</p>
            </div>
        `;
        
        resultContent.innerHTML = resultHTML;
        resultContainer.style.display = 'block';
        
        // 결과 영역으로 스크롤
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
} 