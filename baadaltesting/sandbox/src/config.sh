function config_init
{
  mkdir -p $CONFIG
}

function config_get
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}
  CONFIG_VAL=

  # Get from $CONFIG
  CONFIG_VAL=$(cat $config_file 2>/dev/null)
  if [[ $CONFIG_VAL == "" ]]; then
    # Get default value or value from environment
    CONFIG_VAL=${!config_name}
  fi
  eval $config_name=\$CONFIG_VAL
}

function config_set
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}

  echo "${!config_name}" > $config_file
}

function config_clr
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}

  rm -f $config_file
}
