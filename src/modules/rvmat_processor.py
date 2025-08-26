"""
RVMAT 文件处理器模块
用于快速处理 DayZ 材质 Rvmat 文件
"""

import os


class RvmatProcessor:
    """RVMAT 文件处理器"""
    
    def __init__(self):
        self.texture_mappings = {
            '_worn': r'dz\characters\data\generic_worn_mc.paa',
            '_damage': r'dz\characters\data\generic_damage_mc.paa',
            '_destruct': r'dz\characters\data\generic_destruct_mc.paa'
        }
    
    def is_rvmat_file(self, file_path):
        """检查文件是否为 .rvmat 文件"""
        return file_path.lower().endswith('.rvmat')
    
    def process_rvmat_file(self, input_file):
        """处理 RVMAT 文件并生成三种变体"""
        if not self.is_rvmat_file(input_file):
            print(f"错误: {input_file} 不是有效的 .rvmat 文件")
            return False
        
        try:
            # 读取原文件内容
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件名（不含扩展名）
            base_name = os.path.splitext(input_file)[0]
            
            # 为每种纹理生成文件
            for suffix, texture_path in self.texture_mappings.items():
                self._generate_variant(content, base_name, suffix, texture_path, input_file)
            
            return True
            
        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
            return False
    
    def _generate_variant(self, content, base_name, suffix, texture_path, input_file):
        """生成特定变体的文件"""
        # 替换 Stage3 中的 texture 参数
        modified_content = self._replace_stage3_texture(content, texture_path)
        
        # 生成新文件名
        output_file = f"{base_name}{suffix}.rvmat"
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
    
    def _replace_stage3_texture(self, content, new_texture_path):
        """替换 Stage3 中的 texture 参数"""
        lines = content.split('\n')
        in_stage3 = False
        modified_lines = []
        
        for line in lines:
            # 检查是否进入 Stage3 块
            if 'class Stage3' in line:
                in_stage3 = True
                modified_lines.append(line)
                continue
            
            # 检查是否离开 Stage3 块
            if in_stage3 and line.strip().startswith('};'):
                in_stage3 = False
                modified_lines.append(line)
                continue
            
            # 如果在 Stage3 块中，查找并替换 texture 参数
            if in_stage3 and 'texture=' in line:
                # 替换 texture 路径
                modified_line = line.split('texture=')[0] + f'texture="{new_texture_path}";'
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)
        
        return '\n'.join(modified_lines)