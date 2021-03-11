#
# Expected arguments
#

# GIT_REPOSITORY: GitHub repository URL (e.g., https://github.com/uwscope/scope-web.git)
ARG GIT_REPOSITORY
# GIT_REPOSITORY_BRANCH: Branch to use from GIT_REPOSITORY
ARG GIT_REPOSITORY_BRANCH

#
# Stage arguments
#
# Confirm required arguments.
#
FROM alpine:3 as stage_required

ARG GIT_REPOSITORY
ARG GIT_REPOSITORY_BRANCH

RUN test -n "$GIT_REPOSITORY" || (echo "Argument GIT_REPOSITORY required" && false)
RUN test -n "$GIT_REPOSITORY_BRANCH" || (echo "Argument GIT_REPOSITORY_BRANCH required" && false)

#
# Stage git
#
# Obtain the web source from GitHub.
#
FROM alpine:3 AS stage_git

ARG GIT_REPOSITORY
ARG GIT_REPOSITORY_BRANCH

# Install git. Modeled on alpine/git:
# https://github.com/alpine-docker/git
RUN apk --update add git less openssh && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

# Clone web repository
RUN git clone -b $GIT_REPOSITORY_BRANCH $GIT_REPOSITORY web

#
# Stage serve
#
# Serve the project. Assumptions about the project:
# - Dependencies installed via a `yarn install`.
# - Will then serve via a `yarn serve`.
# - Will listen on port 3000.
#
FROM node:15-alpine AS stage_serve

WORKDIR /web
COPY --from=stage_git /web .
RUN yarn install

EXPOSE 3000
CMD ["yarn", "serve"]
