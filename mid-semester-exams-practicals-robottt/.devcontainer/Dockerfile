FROM osrf/ros:jazzy-desktop

ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi

RUN apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

RUN sudo usermod --append --groups video $USERNAME
RUN sudo apt update && sudo apt upgrade -y
RUN sudo apt install -y git curl
RUN rosdep update
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc

################################
## ADD ANY CUSTOM SETUP BELOW ##
################################

# Pre-install pocketsphinx manually to avoid mirror 403 errors
RUN curl -L -o /tmp/pocketsphinx-en-us.deb \
    https://mirrors.kernel.org/ubuntu/pool/universe/p/pocketsphinx/pocketsphinx-en-us_0.8.0+real5prealpha+1-15ubuntu5_all.deb && \
    sudo dpkg -i /tmp/pocketsphinx-en-us.deb && \
    rm /tmp/pocketsphinx-en-us.deb

# Install Gazebo and ROS-GZ packages
RUN sudo apt update && sudo apt install -y \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    --fix-missing || true

# Install Python dependencies
RUN pip install jinja2 lark pyyaml --break-system-packages
