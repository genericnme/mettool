class Plotconfiguration:
    def __init__(self, cmap='Oranges', grades=15, fill=True):
        self.cmap=cmap
        self.grades=grades
        self.fill=fill

    def set_cmap(self, cmap):
        self.cmap=cmap

    def set_grades(self, grades):
        self.grades = grades

    def set_fill(self, fill):
        self.fill = fill

    def __str__(self):
        return f"Yeah {self.cmap}, {self.grades}"