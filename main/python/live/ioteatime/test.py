from ai_service.main import set_outlier
from ai_service.main import forecast

param_grid = {
    'changepoint_prior_scale' : [0.1, 0.5]
}

print("start: forecast")
forecast(param_grid)

print("start: set outlier")
set_outlier()