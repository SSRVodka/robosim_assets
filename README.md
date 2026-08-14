## Assets Repo for RoboSim


本仓库包含了不同模拟器后端的资源目录。按照模拟器类型区分存放目录，`gazebo-11/assets` 存放 Gazebo Classic 的资源，`mujoco/assets` 存放 MuJoCo 的资源。

现在支持的机器人：

- `gazebo-11/assets/robots/diffdrive_car`
- `mujoco/assets/robots/franka_panda`
- `mujoco/assets/robots/robot_vacuum`
- `mujoco/assets/robots/vx300s_cohesive`
- `mujoco/assets/robots/unitree_g1`

现在支持的场景：

- `gazebo-11/assets/worlds/sdf/aws_house.world`
- `gazebo-11/assets/worlds/sdf/standard_room.classic.world`
- `mujoco/assets/worlds/bedroom`
- `mujoco/assets/worlds/cafe`
- `mujoco/assets/worlds/oldroom`
- `mujoco/assets/worlds/two_bedroom_apartment`



### MuJoCo 资产规约

- `worlds/`：存放的场景入口与场景本地 mesh / texture 资源。默认场景文件名（入口）为 `scene.xml`；

- `robots/`：存放被场景直接引用的机器人模型资源（MJCF 格式）；


> [!NOTE]
>
> 如果您需要为 MuJoCo 后端添加新的机器人，除了需要准备 XML 文件（MJCF）以外，还需要提供一个语义化的 SRDF 文件，用于描述机器人的关节模型组（Joint Model Group）。
> 
> “关节模型组”（JointModelGroup）是完全由用户定义的关节分组（在用户的 SRDF 文件中指定）。每个 JointModelGroup 可以包含 ≥ 0 个末端执行器和 ≥ 0 个固定姿态（组状态）。
> 
> 使用 JointModelGroup 抽象概念，可以非常方便地选择一系列关节和末端执行器进行驱动。这是基于 Moveit2 JointModelGroup 定义的概念。
> 
> 您可以自行手写一份 SRDF 文件，模仿 [`mujoco/assets/robots/franka_panda/panda.srdf`](./mujoco/assets/robots/franka_panda/panda.srdf) 的内容，您可以自由规定哪些关节在一个组里面最方便您之后的操纵。如不提供，robosim 会将所有位于一个 kinematic tree 上的关节放在一个 JointModelGroup 中。
> 
> 您也可以借助 ROS2 Moveit2 官方提供的 wizard（`ros2 run moveit_setup_assistant moveit_set
up_assistant`），导入您的机器人模型，一步步地生成，拿到其中的 `*.srdf` 即可；
