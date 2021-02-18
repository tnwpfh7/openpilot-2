class Steer_Mid_Smoother():
  def __init__(self):
    self.data_steer = [0., 0.]
  def get_data(self, steer_angle_dest, weight):
    self.data_steer.pop(0)
    self.data_steer.append(steer_angle_dest)
    return self.data_steer[0] + (self.data_steer[1] - self.data_steer[0]) * weight
    
class Steer_Idle_Smoother():
  def __init__(self):
    self.data_start = 0
    self.data_start_flg = 0
    self.data_steer = [[0.,0.], [0.,0.]]
    
  def get_data(self, steer_angle_dest, stAngle_Diff, reduceRate):
    self.data_steer[0].pop(0); self.data_steer[1].pop(0)
    self.data_steer[0].append(steer_angle_dest); self.data_steer[1].append(steer_angle_dest)
    
    if abs(self.data_steer[0][1] - self.data_steer[0][0]) >= stAngle_Diff:
      if self.data_start_flg == 0:
        self.data_start = self.data_steer[0][0]
        self.data_start_flg = 1
      if self.data_steer[0][0] * self.data_steer[1][1] < 0:
        self.data_start = (self.data_steer[1][0] + self.data_steer[1][1]) * reduceRate
      data_rst = self.data_start + steer_angle_dest * reduceRate
      self.data_steer[0][1] = data_rst
    else:
      data_rst = steer_angle_dest
      self.data_start_flg = 0
    return data_rstweight