from selfdrive.controls.lib.pid import PIController
from selfdrive.controls.lib.drive_helpers import get_steer_max
from cereal import car
from cereal import log
from selfdrive.kegman_kans_conf import kegman_kans_conf


class LatControlPID():
  def __init__(self, CP):
    self.pid = PIController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                            (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                            k_f=CP.lateralTuning.pid.kf, pos_limit=1.0, neg_limit=-1.0,
                            sat_limit=CP.steerLimitTimer)
#add kegman's config
    self.kegman_kans = kegman_kans_conf(CP)
    self.deadzone = float(self.kegman_kans.conf['deadzone'])

    self.angle_steers_des = 0.
#	
# interpolate sR according to Angle part01
    self.angle_steers_des_last = 0.
    self.angle_steer_rate = [0.25, 0.5, 0.75, 1.0]
    self.angleBP = [7., 14., 23., 35.0]
    self.angle_steer_new = 0.0
  def reset(self):
    self.pid.reset()

  def update(self, active, CS, CP, path_plan):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steerAngle = float(CS.steeringAngle)
    pid_log.steerRate = float(CS.steeringRate)

    if CS.vEgo < 0.3 or not active:
      output_steer = 0.0
      pid_log.active = False
      self.pid.reset()
    else:
      self.angle_steers_des = path_plan.angleSteers  # get from MPC/LateralPlanner
# interpolate sR according to Angle part02
      self.angle_steer_new = interp(CS.vEgo, self.angleBP, self.angle_steer_rate)
      check_pingpong = abs(self.angle_steers_des - self.angle_steers_des_last) > 4.0
      if check_pingpong:
        self.angle_steers_des = path_plan.angleSteers * self.angle_steer_new

      steers_max = get_steer_max(CP, CS.vEgo)
      self.pid.pos_limit = steers_max
      self.pid.neg_limit = -steers_max
      steer_feedforward = self.angle_steers_des   # feedforward desired angle
#
# interpolate sR according to Angle part03
      self.angle_steers_des_last = self.angle_steers_des
      if CP.steerControlType == car.CarParams.SteerControlType.torque:
        # TODO: feedforward something based on path_plan.rateSteers
        steer_feedforward -= path_plan.angleOffset   # subtract the offset, since it does not contribute to resistive torque
#
# interpolate sR according to Angle part04
        _c1, _c2, _c3 = [0.35189607550172824, 7.506201251644202, 69.226826411091]
        steer_feedforward *= _c1 * CS.vEgo ** 2 + _c2 * CS.vEgo + _c3
      deadzone = self.deadzone
      #  steer_feedforward *= CS.vEgo**2  # proportional to realigning tire momentum (~ lateral accel)
      #deadzone = 0.0

      check_saturation = (CS.vEgo > 10) and not CS.steeringRateLimited and not CS.steeringPressed
      output_steer = self.pid.update(self.angle_steers_des, CS.steeringAngle, check_saturation=check_saturation, override=CS.steeringPressed,
                                     feedforward=steer_feedforward, speed=CS.vEgo, deadzone=deadzone)
      pid_log.active = True
      pid_log.p = self.pid.p
      pid_log.i = self.pid.i
      pid_log.f = self.pid.f
      pid_log.output = output_steer
      pid_log.saturated = bool(self.pid.saturated)

    return output_steer, float(self.angle_steers_des), pid_log
