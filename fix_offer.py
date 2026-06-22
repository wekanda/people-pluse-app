#!/usr/bin/env python3
"""Fix broken Offer model in models.py"""

with open('models.py') as f:
    content = f.read()

# Find and replace the broken Offer class
idx = content.find('class Offer(Base):')
if idx != -1:
    # Find end of Offer class (next class or comment)
    end_idx = content.find('# ==================== PHASE 1', idx)
    if end_idx != -1:
        before = content[:idx]
        after = content[end_idx:]
        fixed_offer = '''class Offer(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    position = Column(String)
    salary = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


'''
        content = before + fixed_offer + after
        with open('models.py', 'w') as f:
            f.write(content)
        print('✓ Offer class fixed')
