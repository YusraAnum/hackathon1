---
title: ROS2 Fundamentals
sidebar_label: ROS2 Fundamentals
---

# ROS2 Fundamentals

## Introduction to ROS2

ROS2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.

ROS2 is the next generation of the Robot Operating System, designed to address the limitations of ROS1 and provide features required for production environments, including improved security, real-time support, and better multi-robot systems support.

## Key Features of ROS2

### Middleware Implementation
ROS2 uses DDS (Data Distribution Service) as its underlying middleware, providing:

- **Real-time support**: Critical for time-sensitive robot applications
- **Security**: Authentication, encryption, and access control
- **Multi-vendor support**: Multiple DDS implementations available
- **Distributed systems**: Better support for multi-robot systems

### Node Architecture
In ROS2, nodes are the fundamental unit of execution:

- **Lifecycle management**: Nodes can be configured, activated, and deactivated
- **Namespaces**: Better organization of nodes and topics
- **Parameters**: Dynamic configuration of nodes

### Communication Patterns
ROS2 supports multiple communication patterns:

- **Topics**: Publish-subscribe pattern for streaming data
- **Services**: Request-response pattern for synchronous communication
- **Actions**: Goal-based communication for long-running tasks

## Core Concepts

### Packages and Workspaces
ROS2 organizes code into packages, which are stored in workspaces:

- **Packages**: Contain libraries, executables, scripts, and other files
- **Workspaces**: Directories where packages are built and sourced
- **ament**: The build system used by ROS2

### Quality of Service (QoS)
QoS settings allow fine-tuning of communication behavior:

- **Reliability**: Best effort vs. reliable delivery
- **Durability**: Volatile vs. transient local
- **History**: Keep last N messages vs. keep all messages

## Practical Implementation

### Creating a Simple Publisher
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MinimalPublisher : public rclcpp::Node
{
public:
    MinimalPublisher()
    : Node("minimal_publisher"), count_(0)
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        timer_ = this->create_wall_timer(
            500ms, std::bind(&MinimalPublisher::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello, world! " + std::to_string(count_++);
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t count_;
};
```

## Advantages of ROS2

- **Industry adoption**: Used by major robotics companies
- **Multi-platform support**: Linux, Windows, macOS
- **Large ecosystem**: Extensive libraries and tools
- **Standardized interfaces**: Common message types and services
- **Simulation integration**: Strong integration with Gazebo and other simulators

ROS2 continues to evolve with new distributions released regularly, making it the de facto standard for robotic software development.