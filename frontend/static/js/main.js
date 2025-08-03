// frontend/static/js/main.js
// 사용자 입력 이벤트 핸들링 및 페이지 동작

document.addEventListener('DOMContentLoaded', function() {
    // 페이지 로드 시 초기화
    initializePage();
});

function initializePage() {
    // 관심사 태그 이벤트 리스너 등록
    setupInterestTags();
    
    // 폼 제출 이벤트 리스너 등록
    setupFormSubmission();
    
    // 입력 필드 유효성 검사
    setupValidation();
}

function setupInterestTags() {
    const tags = document.querySelectorAll('.tag');
    
    tags.forEach(tag => {
        tag.addEventListener('click', function() {
            // 최대 5개까지만 선택 가능
            const selectedTags = document.querySelectorAll('.tag.selected');
            
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
            } else if (selectedTags.length < 5) {
                this.classList.add('selected');
            } else {
                showMessage('관심사는 최대 5개까지만 선택할 수 있습니다.', 'warning');
                return;
            }
            
            updateSelectedInterests();
        });
    });
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
        age_range: [
            parseInt(document.getElementById('ageMin').value),
            parseInt(document.getElementById('ageMax').value)
        ],
        location: document.getElementById('location').value,
        interests: getSelectedInterests(),
        style: document.getElementById('style').value,
        height: document.getElementById('height').value
    };
}

function getSelectedInterests() {
    const selectedTags = document.querySelectorAll('.tag.selected');
    return Array.from(selectedTags).map(tag => tag.dataset.value);
}

function updateSelectedInterests() {
    const interests = getSelectedInterests();
    const hiddenInput = document.getElementById('selectedInterests');
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(interests);
    }
}

function validateFormData(data) {
    // 나이 범위 검증
    if (!data.age_range || data.age_range[0] >= data.age_range[1]) {
        showMessage('올바른 나이 범위를 입력해주세요.', 'error');
        return false;
    }
    
    // 지역 검증
    if (!data.location) {
        showMessage('지역을 선택해주세요.', 'error');
        return false;
    }
    
    // 관심사 검증
    if (!data.interests || data.interests.length === 0) {
        showMessage('관심사를 최소 1개 이상 선택해주세요.', 'error');
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
    
    if (ageMin && ageMax && ageMin >= ageMax) {
        document.getElementById('ageMax').setCustomValidity('최대 나이는 최소 나이보다 커야 합니다.');
    } else {
        document.getElementById('ageMax').setCustomValidity('');
    }
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
        submitBtn.textContent = '확률 계산하기';
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
        resultContent.innerHTML = `
            <div class="result-item">
                <h4>매칭 확률: ${result.probability}%</h4>
                <p>희귀도: ${result.rarity_level}</p>
                <p>입력한 조건: ${JSON.stringify(result.filters)}</p>
            </div>
        `;
        
        resultContainer.style.display = 'block';
        
        // 결과 영역으로 스크롤
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
} 