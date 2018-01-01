# lasso
lasso is for roundups


Edit `docker-compose.yml` to include Plaid API secrets, then
```
docker-compose up -d
```


Flower is available at http://localhost:5555 to monitor the the celery tasks


To collect transactions
```
docker exec -it lasso_worker_1 python run_collector.py
```

To round up transactions
```
docker exec -it lasso_worker_1 python run_rancher.py
```
