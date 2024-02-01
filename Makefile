COMPOSE = ./srcs/docker-compose.yml

all:
	@docker-compose -f $(COMPOSE) up -d --build

down:
	@docker-compose -f $(COMPOSE) down

re: fclean all

clean:
	@docker-compose -f $(COMPOSE) down

fclean : clean
	docker rmi $$(docker images -q)

logs:
	@docker-compose -f $(COMPOSE) logs

ps:
	@docker-compose -f $(COMPOSE) ps

ssh:
	@docker-compose -f $(COMPOSE) exec $(s) /bin/bash
