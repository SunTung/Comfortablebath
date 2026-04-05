class RiskScorer:
    def __init__(self, increase_on_suspected=10, decay_idle=5, medium_threshold=40, high_threshold=80):
        self.score = 0
        self.level = "low"
        self.increase_on_suspected = increase_on_suspected
        self.decay_idle = decay_idle
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold

    def update(self, suspected=False):
        if suspected:
            self.score = min(100, self.score + self.increase_on_suspected)
        else:
            self.score = max(0, self.score - self.decay_idle)

        if self.score >= self.high_threshold:
            self.level = "high"
        elif self.score >= self.medium_threshold:
            self.level = "medium"
        else:
            self.level = "low"

        return self.score

    def current_level(self):
        return self.level
