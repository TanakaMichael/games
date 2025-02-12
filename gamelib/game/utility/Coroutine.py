class WaitForSeconds:
    """指定秒数待機する (delta_time ベース)"""
    def __init__(self, seconds):
        self.remaining_time = seconds  # 残り時間

    def update(self, delta_time):
        """delta_time を減算し、待機完了か判定"""
        self.remaining_time -= delta_time
        return self.remaining_time <= 0  # 0以下になったら完了

class Coroutine:
    """実行中のコルーチン"""
    def __init__(self, generator):
        self.generator = generator
        self.done = False
        self.current_wait = None
        self.first_step = True  # **最初のステップかどうかのフラグ**

    def step(self, delta_time):
        """コルーチンを1ステップ進める"""
        try:
            if self.current_wait:
                if not self.current_wait.update(delta_time):
                    return
                self.current_wait = None  # 待機が完了したら解除

            # **最初のステップなら `next()` を使う**
            if self.first_step:
                result = next(self.generator)
                self.first_step = False  # **最初のステップを完了**
            else:
                result = self.generator.send(delta_time)  

            if isinstance(result, WaitForSeconds):
                self.current_wait = result  

        except StopIteration:
            self.done = True  



class CoroutineManager:
    """コルーチンを管理するクラス"""
    def __init__(self):
        self.coroutines = []
    def clear(self):
        """すべてのコルー��ンを停止"""
        self.coroutines = []  # すべてのコルー��ンをリセットする

    def start_coroutine(self, func, *args):
        """関数をコルーチンとして開始"""
        coroutine = Coroutine(func(*args))
        self.coroutines.append(coroutine)
        return coroutine  # Coroutine インスタンスを返す

    def stop_coroutine(self, coroutine):
        """コルーチンを停止"""
        if coroutine in self.coroutines:
            self.coroutines.remove(coroutine)

    def update(self, delta_time):
        """毎フレーム更新 (delta_time ベース)"""
        to_remove = []

        for coroutine in self.coroutines:
            if coroutine.done:
                to_remove.append(coroutine)
                continue
            coroutine.step(delta_time)  # delta_time を考慮して進める

        for coroutine in to_remove:
            self.coroutines.remove(coroutine)
