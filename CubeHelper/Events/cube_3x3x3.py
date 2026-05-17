# Events/cube_3x3x3.py —— 三阶魔方预设
from project_base import Project

class ThreeCubeProject(Project):
    def __init__(self):
        super().__init__(
            name="三阶魔方",
            tags=["CFOP", "七步层先", "出错"]
        )

    def get_input_modes(self):
        return ["单条录入", "批处理", "比赛模式(五次取平均)"]

    def segment_evaluate(self, avg_seconds):
        if avg_seconds is None:
            return None
        comments = {
            'A': "令人惊叹的速度！你已经达到了魔方高手的顶尖水平，每一次转动都透露着专业与从容。保持这份热爱与专注，继续精进，向世界纪录发起冲击！",
            'B': "非常出色的成绩！你已经具备了专业选手的素质，稳定的发挥和扎实的基本功是你最大的优势。不断突破，下一个大师就是你！",
            'C': "你已经超越了大多数魔方爱好者，进入了高手行列。每一次进步都是努力的见证，坚持下去，你会越来越快！",
            'D': "你在魔方道路上稳步前进，这个阶段正是提升的关键时期。多练习，多思考，未来的高手之路就在脚下。",
            'E': "欢迎来到魔方的世界！入门阶段是打基础的好时候，不要灰心，每一次还原都是成长。坚持练习，你一定会看到自己的飞跃。",
            'X': "你的魔方之旅刚刚开始，还有很大的提升空间。别着急，享受每一次还原的乐趣，进步会在不经意间到来。加油！"
        }
        if avg_seconds <= 10:       code, rng, level = "A1", "≤10s", "大师"; comment = comments['A']
        elif avg_seconds <= 12:    code, rng, level = "A2", "10-12s", "大师"; comment = comments['A']
        elif avg_seconds <= 16:    code, rng, level = "A3", "12-16s", "大师"; comment = comments['A']
        elif avg_seconds <= 20:    code, rng, level = "A4", "16-20s", "大师"; comment = comments['A']
        elif avg_seconds <= 25:    code, rng, level = "B1", "20-25s", "专业"; comment = comments['B']
        elif avg_seconds <= 30:    code, rng, level = "B2", "25-30s", "专业"; comment = comments['B']
        elif avg_seconds <= 35:    code, rng, level = "B3", "30-35s", "专业"; comment = comments['B']
        elif avg_seconds <= 40:    code, rng, level = "B4", "35-40s", "专业"; comment = comments['B']
        elif avg_seconds <= 45:    code, rng, level = "C1", "40-45s", "高手"; comment = comments['C']
        elif avg_seconds <= 50:    code, rng, level = "C2", "45-50s", "高手"; comment = comments['C']
        elif avg_seconds <= 60:    code, rng, level = "C3", "50-60s", "高手"; comment = comments['C']
        elif avg_seconds <= 70:    code, rng, level = "C4", "60-70s", "高手"; comment = comments['C']
        elif avg_seconds <= 80:    code, rng, level = "D1", "70-80s", "进阶"; comment = comments['D']
        elif avg_seconds <= 100:   code, rng, level = "D2", "80-100s", "进阶"; comment = comments['D']
        elif avg_seconds <= 120:   code, rng, level = "D3", "100-120s", "进阶"; comment = comments['D']
        elif avg_seconds <= 150:   code, rng, level = "D4", "120-150s", "进阶"; comment = comments['D']
        elif avg_seconds <= 180:   code, rng, level = "E1", "150-180s", "入门"; comment = comments['E']
        elif avg_seconds <= 240:   code, rng, level = "E2", "180-240s", "入门"; comment = comments['E']
        elif avg_seconds <= 300:   code, rng, level = "E3", "240-300s", "入门"; comment = comments['E']
        elif avg_seconds <= 600:   code, rng, level = "E4", "300-600s", "入门"; comment = comments['E']
        else:                      code, rng, level = "—", ">600s", "未入段"; comment = comments['X']
        return {'code': code, 'range': rng, 'level': level, 'comment': comment}

ProjectClass = ThreeCubeProject
