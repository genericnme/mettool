from ipywidgets import Output

dbg = Output()
# Avoiding circular imports. dbg widget is being displayed in View class and captures warnings created in Model class
