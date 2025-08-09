# backend/app/services/image_service.py
# 결과 공유용 이미지 생성 서비스

import os
from typing import Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class ImageService:
    """결과 공유용 이미지 생성 서비스"""
    
    def __init__(self):
        """이미지 서비스 초기화"""
        self.default_width = 800
        self.default_height = 600
        self.background_color = (255, 255, 255)  # 흰색
        self.text_color = (51, 51, 51)  # 진한 회색
        self.accent_color = (255, 105, 180)  # 핑크색
        
    def generate_result_card(self, result_data: Dict) -> str:
        """
        선택률 계산 결과를 바탕으로 공유용 카드 이미지를 생성합니다.
        
        Args:
            result_data (Dict): 선택률 계산 결과 데이터
            
        Returns:
            str: base64로 인코딩된 이미지 데이터
        """
        try:
            # 이미지 생성
            img = Image.new('RGB', (self.default_width, self.default_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # 제목 그리기
            self._draw_title(draw, "이상형 선택률 분석 결과")
            
            # 선택률 정보 그리기
            probability = result_data.get('probability', 0)
            selection_level = result_data.get('selection_level', '알 수 없음')
            self._draw_percentage_info(draw, probability, selection_level)
            
            # 조건 정보 그리기
            filters = result_data.get('filters', {})
            self._draw_filters_info(draw, filters)
            
            # 푸터 정보 그리기
            self._draw_footer(draw)
            
            # 이미지를 base64로 인코딩
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            # 오류 발생 시 기본 이미지 반환
            return self._generate_error_image(str(e))
    
    def _draw_title(self, draw: ImageDraw.Draw, title: str):
        """제목을 그립니다."""
        try:
            # 기본 폰트 사용 (시스템 폰트가 없을 경우 대비)
            font_size = 36
            font = ImageFont.load_default()
            
            # 제목 위치 계산
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.default_width - text_width) // 2
            y = 50
            
            # 제목 그리기
            draw.text((x, y), title, fill=self.accent_color, font=font)
            
        except Exception:
            # 폰트 오류 시 기본 텍스트 그리기
            draw.text((50, 50), title, fill=self.accent_color)
    
    def _draw_percentage_info(self, draw: ImageDraw.Draw, probability: float, selection_level: str):
        """선택률 정보를 그립니다."""
        try:
            font = ImageFont.load_default()
            
            # 선택률 텍스트
            prob_text = f"선택률: {probability:.2f}%"
            level_text = f"등급: {selection_level}"
            
            # 위치 계산
            y_start = 150
            
            # 선택률 정보 그리기
            draw.text((100, y_start), prob_text, fill=self.text_color, font=font)
            draw.text((100, y_start + 40), level_text, fill=self.text_color, font=font)
            
            # 선택률에 따른 색상 변경
            if probability < 1.0:
                color = (255, 0, 0)  # 빨간색 (매우 드문 조건)
            elif probability < 5.0:
                color = (255, 165, 0)  # 주황색 (드문 조건)
            elif probability < 15.0:
                color = (255, 255, 0)  # 노란색 (보통 조건)
            else:
                color = (0, 128, 0)  # 초록색 (흔한 조건)
            
            # 선택률 원형 표시 (간단한 원 그리기)
            center_x = 600
            center_y = y_start + 20
            radius = 30
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        outline=color, width=3)
            
        except Exception:
            # 오류 시 기본 텍스트만 그리기
            draw.text((100, 150), f"선택률: {probability}%", fill=self.text_color)
    
    def _draw_filters_info(self, draw: ImageDraw.Draw, filters: Dict):
        """조건 정보를 그립니다."""
        try:
            font = ImageFont.load_default()
            y_start = 250
            
            # 조건 제목
            draw.text((100, y_start), "입력한 조건:", fill=self.text_color, font=font)
            
            # 조건 목록 그리기
            y_offset = y_start + 40
            for key, value in filters.items():
                if value:  # 값이 있는 조건만 표시
                    condition_text = f"• {key}: {value}"
                    draw.text((120, y_offset), condition_text, fill=self.text_color, font=font)
                    y_offset += 25
                    
                    # 너무 많은 조건이 있을 경우 처리
                    if y_offset > self.default_height - 100:
                        draw.text((120, y_offset), "...", fill=self.text_color, font=font)
                        break
                        
        except Exception:
            # 오류 시 기본 텍스트만 그리기
            draw.text((100, 250), "조건 정보를 표시할 수 없습니다.", fill=self.text_color)
    
    def _draw_footer(self, draw: ImageDraw.Draw):
        """푸터 정보를 그립니다."""
        try:
            font = ImageFont.load_default()
            
            footer_text = "이상형 선택률 계산기 - 통계 기반 이상형 분석 서비스"
            y_position = self.default_height - 50
            
            # 푸터 텍스트 그리기
            draw.text((50, y_position), footer_text, fill=(128, 128, 128), font=font)
            
        except Exception:
            # 오류 시 기본 텍스트만 그리기
            draw.text((50, self.default_height - 50), "이상형 선택률 계산기", fill=(128, 128, 128))
    
    def _generate_error_image(self, error_message: str) -> str:
        """오류 발생 시 기본 이미지를 생성합니다."""
        try:
            img = Image.new('RGB', (self.default_width, self.default_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # 오류 메시지 그리기
            draw.text((100, 200), "이미지 생성 중 오류가 발생했습니다.", fill=(255, 0, 0))
            draw.text((100, 230), error_message, fill=(128, 128, 128))
            
            # base64 인코딩
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception:
            # 최종 오류 시 빈 이미지 반환
            return ""
    
    def save_image_to_file(self, result_data: Dict, filepath: str) -> bool:
        """
        결과 이미지를 파일로 저장합니다.
        
        Args:
            result_data (Dict): 선택률 계산 결과 데이터
            filepath (str): 저장할 파일 경로
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 이미지 생성
            img = Image.new('RGB', (self.default_width, self.default_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # 이미지 구성 요소 그리기
            self._draw_title(draw, "이상형 선택률 분석 결과")
            
            probability = result_data.get('probability', 0)
            selection_level = result_data.get('selection_level', '알 수 없음')
            self._draw_percentage_info(draw, probability, selection_level)
            
            filters = result_data.get('filters', {})
            self._draw_filters_info(draw, filters)
            
            self._draw_footer(draw)
            
            # 파일로 저장
            img.save(filepath, format='PNG')
            return True
            
        except Exception:
            return False


# 전역 인스턴스
image_service = ImageService()


def generate_result_card(result_data: Dict) -> str:
    """
    결과 카드 생성 함수 (외부에서 호출용)
    
    Args:
        result_data (Dict): 선택률 계산 결과 데이터
        
    Returns:
        str: base64로 인코딩된 이미지 데이터
    """
    return image_service.generate_result_card(result_data)


def save_image_to_file(result_data: Dict, filepath: str) -> bool:
    """
    이미지 파일 저장 함수 (외부에서 호출용)
    
    Args:
        result_data (Dict): 선택률 계산 결과 데이터
        filepath (str): 저장할 파일 경로
        
    Returns:
        bool: 저장 성공 여부
    """
    return image_service.save_image_to_file(result_data, filepath) 