<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# Robotics for Forge: how robots build and test cars, and what a small shop can use
2026-10-21. Every figure comes from the source cited next to it. Licences were read from each repo's LICENSE file or the GitHub licence API on 2026-10-21.

## 1. How robots build cars (body-in-white)
- **Robot counts and weld counts.** BMW Regensburg's expanded body shop installed 294 robots. Each X1/X2 body gets up to 4,771 welding operations from 238 robot-mounted welding guns, and the shop builds more than 120 bodies a day. Every robot was modelled as a digital twin before installation [1]. Opel Zaragoza's body shop runs 1,221 robots, which make an average of 3,900 spot welds per vehicle, and 149 on-line cameras check weld quality and dimensions. The same plant uses 79 robots for handling between presses [2]. Stellantis Detroit (Mack) has 578 body-shop robots. 26 of them work in a "net form & pierce" cell that measures gaps, forms the sheet metal and pierces it [3].
- **Where the robots go.** In 2024 the European car industry installed 23,000 industrial robots, about a third of all manufacturing installations in Europe, against 19,200 in North America [4]. US auto installations reached 13,700 units in 2024, used mainly for material handling and machine tending in body and paint shops [5].
- **Takeaway for Forge:** a body shop is a large set of fixed robots doing spot welding and handling, all planned offline (digital twin first). The core software job is offline path planning against a kinematic model with reach and limit checks. That is what the prototype does at small scale.

## 2. How robots help test cars (sled and crash labs)
- Sled automation is mostly closed-loop motion control, not arms. Seattle Safety's ServoSled is servo-hydraulic, uses closed-loop acceleration and pressure feedback and has a frequency response "beyond 250 Hz". Its software "automatically calculates, sets and checks settings", running on off-the-shelf National Instruments hardware [6].
- Dummy (ATD) setup is measured rather than robot-placed. The Humanetics Dummy Positioning System is a portable camera-based optical CMM for positioning dummies in vehicle crash tests, sled tests and static airbag deployments [7]. A Chalmers thesis automated ATD positioning in CAE through the ANSA Python API. Its automatically placed Hybrid III 50th male fell within two standard deviations of physical positioning at five of six X/Z locations [8].
- **Takeaway:** for Forge, "robotics in testing" means repeatable fixturing and pose measurement (an IK/FK model plus metrology), feeding the truth layer. The play layer should never claim crash results.

## 3. What a small shop could use
### Arms
| Arm | Axes / key spec | Licence (repo) | Notes |
|---|---|---|---|
| SO-101 (TheRobotStudio SO-ARM100) | Leader/follower arms built from STS3215 servos | **Apache-2.0** [9] | The README's parts total is $121.94 for one follower arm and $229.88 for a leader plus follower [9]. Driven by LeRobot (Apache-2.0) [10]. Good for learning and teleoperation, not for welding loads. |
| PAROL6 (Source Robotics) | 3D-printed 6-axis desktop arm; ROS 2/MoveIt sim repo exists | **GPL-3.0** (LICENSE file). The README badge is labelled "MIT" but links GPLv3 [11] | Copyleft: keep it out of the MIT codebase and use it only as a separate program. |
| UR5e (Universal Robots, commercial cobot) | 6 joints, 850 mm reach, 5 kg payload, ±0.03 mm repeatability (ISO 9283), ±360° joints except the elbow at ±160° [12] | The ROS 2 description and driver are **BSD-3-Clause** [13] | The DH table is published [14]. This is the arm modelled in the prototype. |
| Franka (franka_ros2) | research arm | **Apache-2.0** [15] | |
| Kinova (ros2_kortex) | research arm | **BSD-3-Clause** text (GitHub shows "NOASSERTION") [16] | |

### Software stack (licence check)
| Project | Licence | Use |
|---|---|---|
| ROS 2 client library rclcpp | Apache-2.0 [17] | middleware |
| ros2_control | Apache-2.0 [18] | hardware interfaces and controllers |
| MoveIt 2 | BSD-3-Clause [19] | motion planning (OMPL, Pilz LIN/CIRC) |
| pymoveit2 | BSD-3-Clause [17] | Python MoveIt 2 interface |
| TRAC-IK | BSD-3-Clause [17] | numerical IK, ROS default alternative |
| opw_kinematics | Apache-2.0 [17] | analytic IK for 6-axis industrial arms |
| Pinocchio | BSD-2-Clause [17] | fast rigid-body kinematics and dynamics (C++/Python) |
| Robotics Toolbox for Python (Corke) | MIT [17] | teaching and prototyping. PAROL6 uses it [11] |
| Tesseract | mixed Apache-2.0 / BSD-2 / BSD-3 [20] | industrial motion planning |
| ROS-Industrial Scan-N-Plan, Noether, REACH, industrial_reconstruction | Apache-2.0 [17][21] | scan, then toolpath, then plan. Adds constant-TCP-speed time parameterisation [22] |
| hold_and_weld (ROS 2 Jazzy, proof of concept) | Apache-2.0 [23] | Extracts weld seams from CAD or meshes and plans with MoveIt 2. Rejects candidates on IK failure, joint limits, low manipulability or large joint steps [24] |
| **orocos KDL** | **LGPL-2.1-or-later** [25] | Avoid in-tree, because it is copyleft |
| Rust `k` (openrr) | Apache-2.0, v0.32.0, depends on nalgebra ^0.30 [26][27] | Pure-Rust URDF, FK and IK. It would bring a second nalgebra next to Rapier's 0.35, so it was not used |
| Rapier 0.36 multibody | Apache-2.0 [28] | Reduced-coordinate joints, plus a built-in damped-Jacobian IK (`multibody_ik.rs`) **with no joint-limit handling** (read in the source) [29] |

**Recommendation.** Keep Forge's kinematics in Rust on Rapier multibodies plus our own limit-aware DLS IK (the prototype). For a real cell, export the same chain as URDF and plan in ROS 2 + MoveIt 2 (BSD/Apache), with TRAC-IK or opw_kinematics for IK. Avoid KDL (LGPL) and PAROL6 code (GPL) in-tree.

## 4. Weld-torch angles used by the prototype
Lincoln Electric's guidance for X-ray quality aluminium GMAW is a 45° work angle and a 10–20° push travel angle [30]. The prototype uses a 45° work angle (bisecting the tube-to-plate corner) and a travel angle that defaults to 0° and can be changed with `--travel-deg`. The tests use 10°, the low end of the cited aluminium range. For steel, follow the welding sector's procedure.

## 5. Prototype (this folder)
See README.md. A UR5e is built as a Rapier f64 multibody from UR's DH table [14]. DLS IK with joint limits follows a straight fillet seam along a box-tube edge, with reach-bound, limit, joint-jump and manipulability checks, and writes a CSV trajectory. The tests check the FK→IK round trip within 1e-6 m and 1e-6 rad, that Rapier and DH agree within 1e-12, and that reach and limit failures are detected.

## Sources
1. BMW Regensburg body shop (Robotics & Automation News, 2025-04-07) https://roboticsandautomationnews.com/2025/04/07/bmw-installs-294-robots-in-major-upgrade-of-factory-in-germany/89625/
2. Opel Zaragoza (Automotive Manufacturing Solutions) https://www.automotivemanufacturingsolutions.com/strategy/small-cars-big-ambitions/539389
3. Stellantis DAC-Mack (Gardner Web) https://www.gardnerweb.com/news/on-the-jeep-grand-cherokee-2022-nissan-pathfinder-and-more
4. IFR press release, 2025-06-17 https://ifr.org/ifr-press-releases/news/europes-auto-industry-installed-23000-new-robots
5. ASSEMBLY, citing IFR https://www.assemblymag.com/articles/99299-american-auto-factories-boost-investment-in-robots
6. Seattle Safety ServoSled https://seattlesafety.com/products/servosled-catapult-sled-systems/
7. Humanetics Dummy Positioning System https://www.humaneticsgroup.com/products/testing-and-measurement-systems/seat-positioning-testing-devices/dummy-positioning-system
8. Chalmers thesis, Automation of ATD positioning for crash analysis simulation https://odr.chalmers.se/items/086f5ae7-ab5d-4e0a-abb6-280de308271b
9. SO-ARM100 LICENSE and README https://github.com/TheRobotStudio/SO-ARM100 (https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/LICENSE)
10. LeRobot https://github.com/huggingface/lerobot
11. PAROL6 LICENSE and README https://github.com/PCrnjak/PAROL6-Desktop-robot-arm (https://raw.githubusercontent.com/PCrnjak/PAROL6-Desktop-robot-arm/main/LICENSE)
12. UR5e technical specifications (SW 5.22 manual) https://www.universal-robots.com/manuals/EN/HTML/SW5_22/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm
13. UR ROS 2 description and driver LICENSE https://github.com/UniversalRobots/Universal_Robots_ROS2_Description ; https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver
14. UR DH parameters https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/
15. franka_ros2 LICENSE https://github.com/frankarobotics/franka_ros2
16. ros2_kortex LICENSE https://github.com/Kinovarobotics/ros2_kortex/blob/main/LICENSE
17. GitHub licence API (2026-10-21): https://api.github.com/repos/ros2/rclcpp , /AndrejOrsula/pymoveit2 , /traclabs/trac_ik , /Jmeyer1292/opw_kinematics , /stack-of-tasks/pinocchio , /petercorke/robotics-toolbox-python , /ros-industrial/reach , /ros-industrial/industrial_reconstruction
18. ros2_control LICENSE https://github.com/ros-controls/ros2_control
19. MoveIt 2 LICENSE https://raw.githubusercontent.com/moveit/moveit2/main/LICENSE.txt
20. Tesseract LICENSE https://github.com/tesseract-robotics/tesseract/blob/master/LICENSE
21. Scan-N-Plan workshop https://github.com/ros-industrial-consortium/scan_n_plan_workshop ; Noether https://github.com/ros-industrial/noether
22. ROS-Industrial, Robotic Blending M5 (constant-TCP-velocity parameterisation) https://rosindustrial.org/news/2024/4/12/open-source-improvements-from-recently-completed-robotic-blending-m5
23. hold_and_weld https://github.com/silanus23/hold_and_weld
24. hold_and_weld v0.3.0 post https://discourse.openrobotics.org/t/hold-and-weld-v0-3-0-configurable-dual-arm-welding-grasping-framework/58628
25. orocos_kdl package.xml and COPYING https://github.com/orocos/orocos_kinematics_dynamics
26. openrr/k https://github.com/openrr/k
27. crates.io k (0.32.0, dependencies) https://crates.io/crates/k
28. Rapier LICENSE https://github.com/dimforge/rapier/blob/master/LICENSE
29. rapier3d 0.36.1 source `src/dynamics/joint/multibody_joint/multibody_ik.rs` https://crates.io/crates/rapier3d
30. Lincoln Electric, Master Class (aluminium GMAW technique) https://www.lincolnelectric.com/en-ZW/Welding-and-Cutting-Resource-Center/Arc-Magazine/Issues/2017-Summer_Issue-Landing-Page/Magazine-Article---Summer17---Master-Class
