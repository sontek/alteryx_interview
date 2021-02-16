- POST /user
  - username
  - first
  - last
  - budget: 100,000

- POST /user/{username}
  - first
  - last
  - budget: 30,000

- POST /stocks/{username}/buy
  - name: ACN
  - total: 20

- POST /stocks/{username}/sell
  - name: ACN
  - total: 20

- PUT /user/{username}/portfolio
  - CSV file upload

- GET /user/{username}/portfolio?date=1/1/17

