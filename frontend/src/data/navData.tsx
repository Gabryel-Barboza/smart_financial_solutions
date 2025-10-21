import { FaHouse, FaFileImport, FaGear } from 'react-icons/fa6';
import { BsClockHistory } from 'react-icons/bs';

export const navItems = [
  { name: 'Dashboard', icon: <FaHouse />, current: true },
  {
    name: 'Novo Upload',
    icon: <FaFileImport />,
    current: false,
  },
  {
    name: 'Histórico',
    icon: <BsClockHistory />,
    current: false,
  },
  {
    name: 'Configurações',
    icon: <FaGear />,
    current: false,
  },
];
