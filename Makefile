all:
	@docker compose -f ./srcs/docker-compose.yml up -d --build

down:
	@docker compose -f ./srcs/docker-compose.yml down

re: fclean all

clean:
	@docker-compose -f srcs/docker-compose.yml down --volumes --remove-orphans

fclean : clean
	docker rmi $$(docker images -q)

logs:
	@docker compose -f ./srcs/docker-compose.yml logs

ps:
	@docker compose -f ./srcs/docker-compose.yml ps

ssh:
	@docker compose -f ./srcs/docker-compose.yml exec $(service) /bin/bash
