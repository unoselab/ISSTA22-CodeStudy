import re

def remove_java_comments(text):
    """
    Java 코드에서 블록 주석(/* ... */)과 라인 주석(// ...)을 제거합니다.
    문자열 리터럴 내의 주석 기호는 보존합니다.
    """
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # 주석은 공백으로 대체
        else:
            return s # 문자열은 그대로 유지

    # 패턴 설명:
    # 1. ("..."): 큰따옴표 문자열 (이스케이프 문자 포함)
    # 2. ('...'): 작은따옴표 문자
    # 3. (/\*.*?\*/): 블록 주석 (여러 줄 가능)
    # 4. (//[^\r\n]*): 라인 주석
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    
    # 정규식 적용
    return re.sub(pattern, replacer, text)

# --- 테스트 ---
code_with_comments = """
public void test() {
    // This is a line comment
    int a = 10; /* This is a block comment */
    String url = "http://example.com"; // This should NOT be removed
}
"""

print(remove_java_comments(code_with_comments))